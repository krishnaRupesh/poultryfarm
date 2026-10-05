from datetime import datetime
from decimal import Decimal
from flask import Blueprint, jsonify, request

from ..models import db, FeedItem, FeedPurchase
from .helpers import (
    active_query,
    decimal_value,
    int_value,
    mark_updated,
    parse_date,
    request_data,
    require_fields,
)

feed_inventory_bp = Blueprint("feed_inventory", __name__)


# -----------------------------------------------------------------------------
# FEED ITEMS (CRUD)
# -----------------------------------------------------------------------------
@feed_inventory_bp.route("/items", methods=["GET"])
def get_feed_items():
    query = active_query(FeedItem).order_by(FeedItem.name.asc())
    items = query.all()
    return jsonify([item.as_dict() for item in items])


@feed_inventory_bp.route("/items/<int:item_id>", methods=["GET"])
def get_feed_item(item_id):
    item = active_query(FeedItem).filter_by(item_id=item_id).first()
    if not item:
        return jsonify({"error": "Feed item not found"}), 404
    return jsonify(item.as_dict())


@feed_inventory_bp.route("/items", methods=["POST"])
def create_feed_item():
    data, error = request_data()
    if error:
        return error

    error = require_fields(data, ["name"])
    if error:
        return error

    name = data["name"].strip()
    existing = FeedItem.query.filter_by(name=name, is_deleted=False).first()
    if existing:
        return jsonify({"error": f"Feed item '{name}' already exists"}), 400

    category = (data.get("category") or "General").strip()
    default_unit = (data.get("default_unit") or "kg").strip()

    reorder_level_kg, err = decimal_value(data.get("reorder_level_kg", 100.0), "reorder_level_kg")
    if err:
        return err

    initial_stock_kg, err = decimal_value(data.get("current_stock_kg", 0.0), "current_stock_kg")
    if err:
        return err

    initial_cost_per_kg, err = decimal_value(data.get("average_cost_per_kg", 0.0), "average_cost_per_kg")
    if err:
        return err

    created_by = (data.get("created_by") or "system").strip()

    item = FeedItem(
        name=name,
        category=category,
        default_unit=default_unit,
        current_stock_kg=initial_stock_kg or Decimal("0.0"),
        average_cost_per_kg=initial_cost_per_kg or Decimal("0.0"),
        reorder_level_kg=reorder_level_kg or Decimal("100.0"),
        created_by=created_by,
        updated_by=created_by,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.as_dict()), 201


@feed_inventory_bp.route("/items/<int:item_id>", methods=["PUT"])
def update_feed_item(item_id):
    item = active_query(FeedItem).filter_by(item_id=item_id).first()
    if not item:
        return jsonify({"error": "Feed item not found"}), 404

    data, error = request_data()
    if error:
        return error

    if "name" in data and data["name"]:
        new_name = data["name"].strip()
        existing = FeedItem.query.filter(
            FeedItem.name == new_name,
            FeedItem.item_id != item_id,
            FeedItem.is_deleted == False
        ).first()
        if existing:
            return jsonify({"error": f"Another feed item with name '{new_name}' exists"}), 400
        item.name = new_name

    if "category" in data and data["category"]:
        item.category = data["category"].strip()

    if "default_unit" in data and data["default_unit"]:
        item.default_unit = data["default_unit"].strip()

    if "reorder_level_kg" in data:
        reorder_kg, err = decimal_value(data["reorder_level_kg"], "reorder_level_kg")
        if err:
            return err
        item.reorder_level_kg = reorder_kg

    if "current_stock_kg" in data:
        stock_kg, err = decimal_value(data["current_stock_kg"], "current_stock_kg")
        if err:
            return err
        item.current_stock_kg = stock_kg

    if "average_cost_per_kg" in data:
        avg_cost, err = decimal_value(data["average_cost_per_kg"], "average_cost_per_kg")
        if err:
            return err
        item.average_cost_per_kg = avg_cost

    updated_by = (data.get("updated_by") or "system").strip()
    mark_updated(item, updated_by=updated_by)

    db.session.commit()
    return jsonify(item.as_dict())


@feed_inventory_bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_feed_item(item_id):
    item = active_query(FeedItem).filter_by(item_id=item_id).first()
    if not item:
        return jsonify({"error": "Feed item not found"}), 404

    item.is_deleted = True
    mark_updated(item, updated_by="system")
    db.session.commit()
    return jsonify({"message": f"Feed item '{item.name}' deleted successfully", "item_id": item_id})


# -----------------------------------------------------------------------------
# FEED PURCHASES (CRUD)
# -----------------------------------------------------------------------------
@feed_inventory_bp.route("/purchases", methods=["GET"])
def get_purchases():
    query = active_query(FeedPurchase)

    item_id = request.args.get("item_id")
    if item_id:
        query = query.filter_by(item_id=item_id)

    start_date = request.args.get("start_date")
    if start_date:
        d, err = parse_date(start_date, "start_date")
        if not err and d:
            query = query.filter(FeedPurchase.purchase_date >= d)

    end_date = request.args.get("end_date")
    if end_date:
        d, err = parse_date(end_date, "end_date")
        if not err and d:
            query = query.filter(FeedPurchase.purchase_date <= d)

    purchases = query.order_by(FeedPurchase.purchase_date.desc(), FeedPurchase.purchase_id.desc()).all()
    return jsonify([p.as_dict() for p in purchases])


@feed_inventory_bp.route("/purchases/<int:purchase_id>", methods=["GET"])
def get_purchase(purchase_id):
    p = active_query(FeedPurchase).filter_by(purchase_id=purchase_id).first()
    if not p:
        return jsonify({"error": "Purchase record not found"}), 404
    return jsonify(p.as_dict())


@feed_inventory_bp.route("/purchases", methods=["POST"])
def record_purchase():
    data, error = request_data()
    if error:
        return error

    error = require_fields(data, ["item_id", "purchase_date", "quantity", "total_cost"])
    if error:
        return error

    item_id, err = int_value(data["item_id"], "item_id")
    if err:
        return err

    item = active_query(FeedItem).filter_by(item_id=item_id).first()
    if not item:
        return jsonify({"error": "Selected feed item does not exist"}), 404

    purchase_date, err = parse_date(data["purchase_date"], "purchase_date")
    if err:
        return err

    quantity_val, err = decimal_value(data["quantity"], "quantity")
    if err:
        return err
    if quantity_val <= 0:
        return jsonify({"error": "Quantity must be greater than zero"}), 400

    total_cost, err = decimal_value(data["total_cost"], "total_cost")
    if err:
        return err
    if total_cost < 0:
        return jsonify({"error": "Total cost cannot be negative"}), 400

    # Convert unit to standard kg:
    unit = (data.get("unit") or "kg").strip().upper()
    if unit in ("MT", "METRIC TON", "TON", "TONS"):
        quantity_kg = quantity_val * Decimal("1000.0")
    elif unit in ("BAG", "BAGS", "BAG (50KG)"):
        quantity_kg = quantity_val * Decimal("50.0")
    else:
        quantity_kg = quantity_val

    cost_per_kg = total_cost / quantity_kg if quantity_kg > 0 else Decimal("0.0")
    created_by = (data.get("created_by") or "system").strip()

    purchase = FeedPurchase(
        item_id=item.item_id,
        purchase_date=purchase_date,
        quantity_kg=quantity_kg,
        cost_per_kg=cost_per_kg,
        total_cost=total_cost,
        vendor_name=data.get("vendor_name"),
        invoice_no=data.get("invoice_no"),
        remarks=data.get("remarks"),
        created_by=created_by,
        updated_by=created_by,
    )

    # Recalculate Weighted Average Cost and update stock:
    old_stock = item.current_stock_kg or Decimal("0.0")
    old_avg = item.average_cost_per_kg or Decimal("0.0")
    new_stock = old_stock + quantity_kg

    if new_stock > 0:
        new_avg = ((old_stock * old_avg) + total_cost) / new_stock
    else:
        new_avg = cost_per_kg

    item.current_stock_kg = new_stock
    item.average_cost_per_kg = round(new_avg, 4)
    mark_updated(item, updated_by=created_by)

    db.session.add(purchase)
    db.session.commit()

    return jsonify({
        "purchase": purchase.as_dict(),
        "updated_item": item.as_dict(),
    }), 201


@feed_inventory_bp.route("/purchases/<int:purchase_id>", methods=["PUT"])
def update_purchase(purchase_id):
    purchase = active_query(FeedPurchase).filter_by(purchase_id=purchase_id).first()
    if not purchase:
        return jsonify({"error": "Purchase not found"}), 404

    data, error = request_data()
    if error:
        return error

    if "purchase_date" in data:
        p_date, err = parse_date(data["purchase_date"], "purchase_date")
        if err:
            return err
        purchase.purchase_date = p_date

    if "vendor_name" in data:
        purchase.vendor_name = data["vendor_name"]
    if "invoice_no" in data:
        purchase.invoice_no = data["invoice_no"]
    if "remarks" in data:
        purchase.remarks = data["remarks"]

    updated_by = (data.get("updated_by") or "system").strip()
    mark_updated(purchase, updated_by=updated_by)

    db.session.commit()
    return jsonify(purchase.as_dict())


@feed_inventory_bp.route("/purchases/<int:purchase_id>", methods=["DELETE"])
def delete_purchase(purchase_id):
    purchase = active_query(FeedPurchase).filter_by(purchase_id=purchase_id).first()
    if not purchase:
        return jsonify({"error": "Purchase not found"}), 404

    # Deduct stock for deleted purchase
    item = purchase.item
    if item:
        item.current_stock_kg = max(Decimal("0.0"), (item.current_stock_kg or Decimal("0.0")) - purchase.quantity_kg)
        mark_updated(item, updated_by="system")

    purchase.is_deleted = True
    mark_updated(purchase, updated_by="system")
    db.session.commit()
    return jsonify({"message": "Purchase deleted successfully", "purchase_id": purchase_id})
