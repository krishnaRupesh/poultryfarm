from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import Blueprint, jsonify, request

from ..models import (
    DailyEggOperation,
    DailyFeedConsumption,
    DailyFlockStatus,
    FeedItem,
    Product,
    FlockBatch,
    Shed,
)
from .helpers import active_query, parse_date

cost_analysis_bp = Blueprint("cost_analysis", __name__)


def _get_analysis_for_date(target_date: date, batch_id: int = None, shed_id: int = None):
    # 1. Flock count
    flock_q = active_query(DailyFlockStatus).filter(DailyFlockStatus.date <= target_date)
    if batch_id:
        flock_q = flock_q.filter_by(batch_id=batch_id)
    elif shed_id:
        flock_q = flock_q.filter_by(shed_id=shed_id)

    flock_rec = flock_q.order_by(DailyFlockStatus.date.desc()).first()

    # Fallback if specific batch has current_birds
    if not flock_rec and batch_id:
        b = active_query(FlockBatch).filter_by(batch_id=batch_id).first()
        active_birds = b.current_birds if b else 0
        mortality = 0
    else:
        active_birds = flock_rec.active_birds if flock_rec else 0
        mortality = flock_rec.mortality if (flock_rec and flock_rec.date == target_date) else 0

    # 2. Feed consumption for target_date
    feed_q = active_query(DailyFeedConsumption).filter_by(date=target_date)
    if batch_id:
        feed_q = feed_q.filter_by(batch_id=batch_id)
    elif shed_id:
        feed_q = feed_q.filter_by(shed_id=shed_id)

    consumptions = feed_q.all()

    feed_items_list = []
    total_feed_kg = Decimal("0.0")
    total_feed_cost = Decimal("0.0")

    for c in consumptions:
        qty_kg = Decimal(str(c.quantity_kg or 0.0))
        cost = Decimal(str(c.total_cost or 0.0))
        unit_cost = Decimal(str(c.cost_per_kg or 0.0))
        total_feed_kg += qty_kg
        total_feed_cost += cost

        feed_items_list.append({
            "consumption_id": c.consumption_id,
            "item_id": c.item_id,
            "item_name": c.item.name if c.item else f"Item #{c.item_id}",
            "category": c.item.category if c.item else "General",
            "quantity_kg": float(qty_kg),
            "quantity_mt": round(float(qty_kg) / 1000.0, 3),
            "cost_per_kg": float(unit_cost),
            "cost_per_mt": round(float(unit_cost) * 1000.0, 2),
            "total_cost": float(cost),
            "batch_id": c.batch_id,
            "batch_name": c.batch.batch_name if c.batch else None,
            "remarks": c.remarks,
        })

    # Add percentage shares
    for item in feed_items_list:
        item["pct_of_cost"] = (
            round((item["total_cost"] / float(total_feed_cost)) * 100, 1)
            if total_feed_cost > 0
            else 0.0
        )
        item["pct_of_weight"] = (
            round((item["quantity_kg"] / float(total_feed_kg)) * 100, 1)
            if total_feed_kg > 0
            else 0.0
        )

    # 3. Metrics per bird
    feed_cost_per_bird = (
        round(float(total_feed_cost) / active_birds, 4)
        if active_birds > 0
        else 0.0
    )
    feed_grams_per_bird = (
        round((float(total_feed_kg) * 1000.0) / active_birds, 1)
        if active_birds > 0
        else 0.0
    )

    # 4. Egg operations
    egg_q = active_query(DailyEggOperation).filter_by(date=target_date)
    if batch_id:
        egg_q = egg_q.filter_by(batch_id=batch_id)
    elif shed_id:
        egg_q = egg_q.filter_by(shed_id=shed_id)

    egg_op = egg_q.first()

    eggs_produced = egg_op.eggs_produced if egg_op else 0
    damaged_eggs = egg_op.damaged_eggs if egg_op else 0
    opening_stock = egg_op.opening_stock if egg_op else 0
    eggs_available = egg_op.eggs_available if egg_op else max(0, opening_stock + eggs_produced - damaged_eggs)
    eggs_sold = egg_op.eggs_sold if egg_op else 0
    closing_stock = egg_op.closing_stock if egg_op else (eggs_available - eggs_sold)

    # Selling price
    if egg_op and egg_op.egg_price_per_unit:
        egg_selling_price = float(egg_op.egg_price_per_unit)
    else:
        egg_product = (
            Product.query.filter(
                Product.product_name.ilike("%egg%"),
                Product.date <= target_date,
                Product.is_deleted == False
            )
            .order_by(Product.date.desc())
            .first()
        )
        egg_selling_price = float(egg_product.price) if (egg_product and egg_product.price) else 0.0

    actual_revenue = (
        float(egg_op.actual_revenue)
        if (egg_op and egg_op.actual_revenue is not None)
        else round(eggs_sold * egg_selling_price, 2)
    )

    # 5. Production Cost per Egg Generated
    production_cost_per_egg = (
        round(float(total_feed_cost) / eggs_produced, 4)
        if eggs_produced > 0
        else 0.0
    )

    # 6. Commercial Profitability Analysis
    profit_margin_per_egg = round(egg_selling_price - production_cost_per_egg, 4)
    realized_gross_profit = round(eggs_sold * profit_margin_per_egg, 2)
    unsold_inventory_value = round(closing_stock * production_cost_per_egg, 2)
    daily_feed_cash_flow = round(actual_revenue - float(total_feed_cost), 2)

    laying_percentage = (
        round((eggs_produced / active_birds) * 100, 2)
        if active_birds > 0
        else 0.0
    )
    sales_rate_pct = (
        round((eggs_sold / eggs_produced) * 100, 1)
        if eggs_produced > 0
        else 0.0
    )

    # 7. Multi-Shed / Batch Breakdown Comparison
    batch_breakdown = []
    batches = active_query(FlockBatch).filter_by(status="Active").all()
    for b in batches:
        b_flock = (
            active_query(DailyFlockStatus)
            .filter(DailyFlockStatus.batch_id == b.batch_id, DailyFlockStatus.date <= target_date)
            .order_by(DailyFlockStatus.date.desc())
            .first()
        )
        b_birds = b_flock.active_birds if b_flock else b.current_birds
        b_mortality = b_flock.mortality if (b_flock and b_flock.date == target_date) else 0

        # Feed for this batch
        b_consumptions = active_query(DailyFeedConsumption).filter_by(date=target_date, batch_id=b.batch_id).all()
        b_feed_cost = sum(float(c.total_cost or 0.0) for c in b_consumptions)
        b_feed_kg = sum(float(c.quantity_kg or 0.0) for c in b_consumptions)

        # Egg ops for this batch
        b_egg = active_query(DailyEggOperation).filter_by(date=target_date, batch_id=b.batch_id).first()
        b_eggs_produced = b_egg.eggs_produced if b_egg else 0
        b_lay_pct = round((b_eggs_produced / b_birds) * 100, 2) if b_birds > 0 else 0.0
        b_cost_per_bird = round(b_feed_cost / b_birds, 4) if b_birds > 0 else 0.0
        b_cost_per_egg = round(b_feed_cost / b_eggs_produced, 4) if b_eggs_produced > 0 else 0.0

        batch_breakdown.append({
            "batch_id": b.batch_id,
            "batch_name": b.batch_name,
            "shed_id": b.shed_id,
            "shed_name": b.shed.shed_name if b.shed else "Unassigned",
            "breed": b.breed,
            "age_weeks": b.age_weeks,
            "active_birds": b_birds,
            "mortality": b_mortality,
            "feed_kg": round(b_feed_kg, 1),
            "feed_cost": round(b_feed_cost, 2),
            "feed_cost_per_bird": b_cost_per_bird,
            "eggs_produced": b_eggs_produced,
            "laying_percentage": b_lay_pct,
            "cost_per_egg": b_cost_per_egg,
        })

    return {
        "date": target_date.isoformat(),
        "batch_id": batch_id,
        "shed_id": shed_id,
        "flock": {
            "active_birds": active_birds,
            "mortality": mortality,
        },
        "feed": {
            "items": feed_items_list,
            "total_feed_kg": float(total_feed_kg),
            "total_feed_mt": round(float(total_feed_kg) / 1000.0, 3),
            "total_feed_cost": round(float(total_feed_cost), 2),
            "feed_cost_per_bird": feed_cost_per_bird,
            "feed_grams_per_bird": feed_grams_per_bird,
        },
        "production": {
            "eggs_produced": eggs_produced,
            "damaged_eggs": damaged_eggs,
            "laying_percentage": laying_percentage,
            "production_cost_per_egg": production_cost_per_egg,
        },
        "sales_and_stock": {
            "opening_stock": opening_stock,
            "eggs_available": eggs_available,
            "eggs_sold": eggs_sold,
            "closing_stock": closing_stock,
            "sales_rate_pct": sales_rate_pct,
            "egg_selling_price": egg_selling_price,
            "actual_revenue": actual_revenue,
            "unsold_inventory_value": unsold_inventory_value,
        },
        "profitability": {
            "profit_margin_per_egg": profit_margin_per_egg,
            "realized_gross_profit": realized_gross_profit,
            "daily_feed_cash_flow": daily_feed_cash_flow,
            "is_profitable": profit_margin_per_egg > 0,
        },
        "batch_breakdown": batch_breakdown,
    }


@cost_analysis_bp.route("/daily", methods=["GET"])
def get_daily_analysis():
    """
    Get comprehensive daily cost-per-bird and cost-per-egg profitability analysis
    ---
    tags:
      - Cost Analysis
    parameters:
      - in: query
        name: date
        type: string
        format: date
        required: false
      - in: query
        name: batch_id
        type: integer
        required: false
      - in: query
        name: shed_id
        type: integer
        required: false
    responses:
      200:
        description: Detailed daily analysis
    """
    date_str = request.args.get("date")
    if date_str:
        target_date, err = parse_date(date_str, "date")
        if err:
            return err
    else:
        latest_op = active_query(DailyEggOperation).order_by(DailyEggOperation.date.desc()).first()
        latest_c = active_query(DailyFeedConsumption).order_by(DailyFeedConsumption.date.desc()).first()
        dates = [d for d in [latest_op.date if latest_op else None, latest_c.date if latest_c else None] if d]
        target_date = max(dates) if dates else date.today()

    batch_id = int(request.args.get("batch_id")) if request.args.get("batch_id") else None
    shed_id = int(request.args.get("shed_id")) if request.args.get("shed_id") else None

    result = _get_analysis_for_date(target_date, batch_id=batch_id, shed_id=shed_id)
    return jsonify(result)


@cost_analysis_bp.route("/history", methods=["GET"])
def get_analysis_history():
    """
    Get historical multi-day comparative cost-per-egg vs selling price trends
    ---
    tags:
      - Cost Analysis
    parameters:
      - in: query
        name: days
        type: integer
        required: false
        default: 7
    responses:
      200:
        description: Trend series
    """
    days = int(request.args.get("days", 7))
    days = min(max(days, 1), 60)

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    history = []
    current = start_date
    while current <= end_date:
        res = _get_analysis_for_date(current)
        history.append({
            "date": current.isoformat(),
            "cost_per_egg": res["production"]["production_cost_per_egg"],
            "selling_price": res["sales_and_stock"]["egg_selling_price"],
            "profit_margin": res["profitability"]["profit_margin_per_egg"],
            "laying_percentage": res["production"]["laying_percentage"],
            "realized_profit": res["profitability"]["realized_gross_profit"],
            "active_birds": res["flock"]["active_birds"],
            "eggs_produced": res["production"]["eggs_produced"],
            "eggs_sold": res["sales_and_stock"]["eggs_sold"],
            "feed_cost": res["feed"]["total_feed_cost"],
        })
        current += timedelta(days=1)

    return jsonify(history)
