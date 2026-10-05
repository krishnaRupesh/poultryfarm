from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import Blueprint, jsonify, request

from ..models import (
    db,
    DailyEggOperation,
    DailyFeedConsumption,
    DailyFlockStatus,
    FeedItem,
    Product,
)
from .helpers import (
    active_query,
    decimal_value,
    int_value,
    mark_updated,
    parse_date,
    request_data,
    require_fields,
)

daily_operations_bp = Blueprint("daily_operations", __name__)


# -----------------------------------------------------------------------------
# 1. DAILY FLOCK STATUS
# -----------------------------------------------------------------------------
@daily_operations_bp.route("/flock", methods=["GET"])
def get_flock():
    target_date = request.args.get("date")
    if target_date:
        d, err = parse_date(target_date, "date")
        if err:
            return err
        flock = active_query(DailyFlockStatus).filter_by(date=d).first()
        if flock:
            return jsonify(flock.as_dict())
        # If no specific record for target_date, find the most recent prior date
        latest = (
            active_query(DailyFlockStatus)
            .filter(DailyFlockStatus.date <= d)
            .order_by(DailyFlockStatus.date.desc())
            .first()
        )
        if latest:
            return jsonify(latest.as_dict())
        return jsonify({"date": str(d), "active_birds": 0, "mortality": 0, "status_id": None})

    # Return list of all flock records
    records = active_query(DailyFlockStatus).order_by(DailyFlockStatus.date.desc()).all()
    return jsonify([r.as_dict() for r in records])


@daily_operations_bp.route("/flock", methods=["POST"])
def record_flock():
    data, error = request_data()
    if error:
        return error

    error = require_fields(data, ["date", "active_birds"])
    if error:
        return error

    flock_date, err = parse_date(data["date"], "date")
    if err:
        return err

    active_birds, err = int_value(data["active_birds"], "active_birds")
    if err:
        return err
    if active_birds < 0:
        return jsonify({"error": "Active birds cannot be negative"}), 400

    mortality = 0
    if "mortality" in data and data["mortality"] not in (None, ""):
        mortality, err = int_value(data["mortality"], "mortality")
        if err:
            return err

    remarks = data.get("remarks")
    created_by = (data.get("created_by") or "system").strip()

    existing = DailyFlockStatus.query.filter_by(date=flock_date, is_deleted=False).first()
    if existing:
        existing.active_birds = active_birds
        existing.mortality = mortality
        existing.remarks = remarks
        mark_updated(existing, updated_by=created_by)
        db.session.commit()
        return jsonify(existing.as_dict())

    flock = DailyFlockStatus(
        date=flock_date,
        active_birds=active_birds,
        mortality=mortality,
        remarks=remarks,
        created_by=created_by,
        updated_by=created_by,
    )
    db.session.add(flock)
    db.session.commit()
    return jsonify(flock.as_dict()), 201


# -----------------------------------------------------------------------------
# 2. DAILY FEED CONSUMPTION
# -----------------------------------------------------------------------------
@daily_operations_bp.route("/consumption", methods=["GET"])
def get_feed_consumption():
    query = active_query(DailyFeedConsumption)
    target_date = request.args.get("date")
    if target_date:
        d, err = parse_date(target_date, "date")
        if err:
            return err
        query = query.filter_by(date=d)

    item_id = request.args.get("item_id")
    if item_id:
        query = query.filter_by(item_id=item_id)

    records = query.order_by(DailyFeedConsumption.date.desc(), DailyFeedConsumption.consumption_id.desc()).all()
    return jsonify([r.as_dict() for r in records])


@daily_operations_bp.route("/consumption", methods=["POST"])
def record_feed_consumption():
    data, error = request_data()
    if error:
        return error

    consumption_date, err = parse_date(data.get("date"), "date")
    if err or not consumption_date:
        return jsonify({"error": "date is required and must be YYYY-MM-DD"}), 400

    items_list = data.get("items")
    # Supports both a batch list of items: [{item_id, quantity, unit}] or single record
    if not items_list:
        error = require_fields(data, ["item_id", "quantity"])
        if error:
            return error
        items_list = [data]

    created_records = []
    created_by = (data.get("created_by") or "system").strip()

    for item_entry in items_list:
        item_id, err = int_value(item_entry.get("item_id"), "item_id")
        if err:
            return err

        item = active_query(FeedItem).filter_by(item_id=item_id).first()
        if not item:
            return jsonify({"error": f"Feed item ID {item_id} not found"}), 404

        qty_val, err = decimal_value(item_entry.get("quantity"), "quantity")
        if err or qty_val <= 0:
            return jsonify({"error": f"Invalid quantity for {item.name}"}), 400

        unit = (item_entry.get("unit") or "kg").strip().upper()
        if unit in ("MT", "METRIC TON", "TON", "TONS"):
            quantity_kg = qty_val * Decimal("1000.0")
        elif unit in ("BAG", "BAGS", "BAG (50KG)"):
            quantity_kg = qty_val * Decimal("50.0")
        else:
            quantity_kg = qty_val

        # Cost per kg from inventory or manual override
        if item_entry.get("cost_per_kg") not in (None, ""):
            cost_per_kg, err = decimal_value(item_entry.get("cost_per_kg"), "cost_per_kg")
            if err:
                return err
        else:
            cost_per_kg = item.average_cost_per_kg or Decimal("0.0")

        total_cost = round(quantity_kg * cost_per_kg, 2)

        # Deduct from inventory stock:
        item.current_stock_kg = max(Decimal("0.0"), (item.current_stock_kg or Decimal("0.0")) - quantity_kg)
        mark_updated(item, updated_by=created_by)

        record = DailyFeedConsumption(
            date=consumption_date,
            item_id=item.item_id,
            quantity_kg=quantity_kg,
            cost_per_kg=cost_per_kg,
            total_cost=total_cost,
            remarks=item_entry.get("remarks"),
            created_by=created_by,
            updated_by=created_by,
        )
        db.session.add(record)
        created_records.append(record)

    db.session.commit()
    return jsonify([r.as_dict() for r in created_records]), 201


@daily_operations_bp.route("/consumption/<int:consumption_id>", methods=["DELETE"])
def delete_feed_consumption(consumption_id):
    rec = active_query(DailyFeedConsumption).filter_by(consumption_id=consumption_id).first()
    if not rec:
        return jsonify({"error": "Consumption record not found"}), 404

    # Restore inventory stock
    item = rec.item
    if item:
        item.current_stock_kg = (item.current_stock_kg or Decimal("0.0")) + rec.quantity_kg
        mark_updated(item, updated_by="system")

    rec.is_deleted = True
    mark_updated(rec, updated_by="system")
    db.session.commit()
    return jsonify({"message": "Feed consumption record deleted", "consumption_id": consumption_id})


# -----------------------------------------------------------------------------
# 3. DAILY EGG OPERATIONS
# -----------------------------------------------------------------------------
@daily_operations_bp.route("/egg-operations/latest-stock", methods=["GET"])
def get_latest_egg_stock():
    target_date = request.args.get("date")
    if target_date:
        d, err = parse_date(target_date, "date")
        if not err and d:
            prior_record = (
                active_query(DailyEggOperation)
                .filter(DailyEggOperation.date < d)
                .order_by(DailyEggOperation.date.desc())
                .first()
            )
            if prior_record:
                return jsonify({
                    "prior_date": str(prior_record.date),
                    "closing_stock": prior_record.closing_stock,
                })

    # Latest record in entire table
    latest = active_query(DailyEggOperation).order_by(DailyEggOperation.date.desc()).first()
    if latest:
        return jsonify({
            "prior_date": str(latest.date),
            "closing_stock": latest.closing_stock,
        })
    return jsonify({"prior_date": None, "closing_stock": 0})


@daily_operations_bp.route("/egg-operations", methods=["GET"])
def get_egg_operations():
    query = active_query(DailyEggOperation)

    target_date = request.args.get("date")
    if target_date:
        d, err = parse_date(target_date, "date")
        if not err and d:
            query = query.filter_by(date=d)

    start_date = request.args.get("start_date")
    if start_date:
        d, err = parse_date(start_date, "start_date")
        if not err and d:
            query = query.filter(DailyEggOperation.date >= d)

    end_date = request.args.get("end_date")
    if end_date:
        d, err = parse_date(end_date, "end_date")
        if not err and d:
            query = query.filter(DailyEggOperation.date <= d)

    records = query.order_by(DailyEggOperation.date.desc()).all()
    return jsonify([r.as_dict() for r in records])


@daily_operations_bp.route("/egg-operations", methods=["POST"])
def record_egg_operations():
    data, error = request_data()
    if error:
        return error

    error = require_fields(data, ["date", "eggs_produced"])
    if error:
        return error

    op_date, err = parse_date(data["date"], "date")
    if err:
        return err

    eggs_produced, err = int_value(data["eggs_produced"], "eggs_produced")
    if err:
        return err
    if eggs_produced < 0:
        return jsonify({"error": "Eggs produced cannot be negative"}), 400

    damaged_eggs = 0
    if "damaged_eggs" in data and data["damaged_eggs"] not in (None, ""):
        damaged_eggs, err = int_value(data["damaged_eggs"], "damaged_eggs")
        if err:
            return err
        if damaged_eggs < 0:
            return jsonify({"error": "Damaged eggs cannot be negative"}), 400

    # Opening stock: from input or previous closing stock
    if "opening_stock" in data and data["opening_stock"] not in (None, ""):
        opening_stock, err = int_value(data["opening_stock"], "opening_stock")
        if err:
            return err
    else:
        prior = (
            active_query(DailyEggOperation)
            .filter(DailyEggOperation.date < op_date)
            .order_by(DailyEggOperation.date.desc())
            .first()
        )
        opening_stock = prior.closing_stock if prior else 0

    eggs_available = max(0, opening_stock + eggs_produced - damaged_eggs)

    # Actual eggs sold: defaults to 0 or entered value
    if "eggs_sold" in data and data["eggs_sold"] not in (None, ""):
        eggs_sold, err = int_value(data["eggs_sold"], "eggs_sold")
        if err:
            return err
        if eggs_sold < 0:
            return jsonify({"error": "Eggs sold cannot be negative"}), 400
    else:
        eggs_sold = 0

    closing_stock = eggs_available - eggs_sold

    # Today's egg selling price per unit:
    # Supports passing price directly per single egg, or per dozen / per 100 / per tray
    price_val = data.get("egg_price_per_unit")
    price_unit = (data.get("price_unit") or "per_egg").lower()

    if price_val not in (None, ""):
        raw_price, err = decimal_value(price_val, "egg_price_per_unit")
        if err:
            return err
        if price_unit in ("per_tray", "tray", "30"):
            egg_price_per_unit = round(raw_price / Decimal("30.0"), 4)
        elif price_unit in ("per_hundred", "100"):
            egg_price_per_unit = round(raw_price / Decimal("100.0"), 4)
        elif price_unit in ("per_dozen", "dozen", "12"):
            egg_price_per_unit = round(raw_price / Decimal("12.0"), 4)
        else:
            egg_price_per_unit = round(raw_price, 4)
    else:
        # Check if an egg product rate exists for this date
        egg_product = (
            Product.query.filter(
                Product.product_name.ilike("%egg%"),
                Product.date <= op_date,
                Product.is_deleted == False
            )
            .order_by(Product.date.desc())
            .first()
        )
        if egg_product and egg_product.price:
            egg_price_per_unit = Decimal(str(egg_product.price))
        else:
            egg_price_per_unit = Decimal("0.0")

    actual_revenue = round(Decimal(str(eggs_sold)) * egg_price_per_unit, 2)
    remarks = data.get("remarks")
    created_by = (data.get("created_by") or "system").strip()

    existing = DailyEggOperation.query.filter_by(date=op_date, is_deleted=False).first()
    if existing:
        existing.opening_stock = opening_stock
        existing.eggs_produced = eggs_produced
        existing.damaged_eggs = damaged_eggs
        existing.eggs_available = eggs_available
        existing.eggs_sold = eggs_sold
        existing.closing_stock = closing_stock
        existing.egg_price_per_unit = egg_price_per_unit
        existing.actual_revenue = actual_revenue
        existing.remarks = remarks
        mark_updated(existing, updated_by=created_by)
        db.session.commit()
        return jsonify(existing.as_dict())

    op = DailyEggOperation(
        date=op_date,
        opening_stock=opening_stock,
        eggs_produced=eggs_produced,
        damaged_eggs=damaged_eggs,
        eggs_available=eggs_available,
        eggs_sold=eggs_sold,
        closing_stock=closing_stock,
        egg_price_per_unit=egg_price_per_unit,
        actual_revenue=actual_revenue,
        remarks=remarks,
        created_by=created_by,
        updated_by=created_by,
    )
    db.session.add(op)
    db.session.commit()
    return jsonify(op.as_dict()), 201


@daily_operations_bp.route("/egg-operations/<int:record_id>", methods=["DELETE"])
def delete_egg_operations(record_id):
    rec = active_query(DailyEggOperation).filter_by(record_id=record_id).first()
    if not rec:
        return jsonify({"error": "Record not found"}), 404

    rec.is_deleted = True
    mark_updated(rec, updated_by="system")
    db.session.commit()
    return jsonify({"message": "Egg operations record deleted", "record_id": record_id})
