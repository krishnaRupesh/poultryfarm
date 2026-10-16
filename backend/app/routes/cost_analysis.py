from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import Blueprint, jsonify, request

from ..models import (
    DailyEggOperation,
    DailyFeedConsumption,
    DailyFlockStatus,
    FeedItem,
    Product,
)
from .helpers import active_query, parse_date

cost_analysis_bp = Blueprint("cost_analysis", __name__)


def _get_analysis_for_date(target_date: date):
    # 1. Flock count
    flock_rec = (
        active_query(DailyFlockStatus)
        .filter(DailyFlockStatus.date <= target_date)
        .order_by(DailyFlockStatus.date.desc())
        .first()
    )
    active_birds = flock_rec.active_birds if flock_rec else 0
    mortality = flock_rec.mortality if (flock_rec and flock_rec.date == target_date) else 0

    # 2. Feed consumption for target_date
    consumptions = (
        active_query(DailyFeedConsumption)
        .filter_by(date=target_date)
        .all()
    )

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
    egg_op = (
        active_query(DailyEggOperation)
        .filter_by(date=target_date)
        .first()
    )

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
        # Fallback to products table egg rate
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

    return {
        "date": target_date.isoformat(),
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
        description: Date for analysis (YYYY-MM-DD, defaults to latest recorded date)
    responses:
      200:
        description: Detailed daily analysis including feed cost per bird, production cost per egg, realized sales profit, and diet breakdown
    """
    date_str = request.args.get("date")
    if date_str:
        target_date, err = parse_date(date_str, "date")
        if err:
            return err
    else:
        # Default to latest date from consumption or egg ops or today
        latest_op = active_query(DailyEggOperation).order_by(DailyEggOperation.date.desc()).first()
        latest_c = active_query(DailyFeedConsumption).order_by(DailyFeedConsumption.date.desc()).first()
        dates = [d for d in [latest_op.date if latest_op else None, latest_c.date if latest_c else None] if d]
        target_date = max(dates) if dates else date.today()

    result = _get_analysis_for_date(target_date)
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
        default: 14
        description: Number of recent days to return
      - in: query
        name: start_date
        type: string
        format: date
        required: false
        description: Custom start date (YYYY-MM-DD)
      - in: query
        name: end_date
        type: string
        format: date
        required: false
        description: Custom end date (YYYY-MM-DD)
    responses:
      200:
        description: Array of daily analytical metrics over the specified time range
    """
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    days_count = request.args.get("days", 14, type=int)

    if end_date_str:
        end_d, err = parse_date(end_date_str, "end_date")
        if err:
            return err
    else:
        end_d = date.today()

    if start_date_str:
        start_d, err = parse_date(start_date_str, "start_date")
        if err:
            return err
    else:
        start_d = end_d - timedelta(days=days_count - 1)

    cur = start_d
    history = []
    while cur <= end_d:
        analysis = _get_analysis_for_date(cur)
        # Only include dates that have either feed consumption or egg production recorded
        if analysis["feed"]["total_feed_cost"] > 0 or analysis["production"]["eggs_produced"] > 0:
            history.append(analysis)
        cur += timedelta(days=1)

    return jsonify(history)
