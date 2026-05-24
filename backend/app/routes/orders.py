from datetime import date

from flask import Blueprint, jsonify

from ..models import Customer, Order, Product, db
from .helpers import (
    active_query,
    decimal_value,
    int_value,
    mark_updated,
    parse_date,
    request_data,
    require_fields,
)


orders_bp = Blueprint("orders", __name__)


def _product_price(product_id, order_date):
    return Product.query.filter_by(
        product_id=product_id,
        date=order_date,
        is_deleted=False,
    ).first()


def _calculate_total(price, discount_price, quantity):
    effective_price = discount_price if discount_price is not None else price
    return effective_price * quantity


@orders_bp.route("/", methods=["GET"])
def get_orders():
    orders = active_query(Order).order_by(Order.date.desc(), Order.order_id.desc()).all()
    return jsonify([order.as_dict() for order in orders])


@orders_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.as_dict())


@orders_bp.route("/", methods=["POST"])
def add_order():
    data, error = request_data()
    if error:
        return error

    error = require_fields(data, ["customer_id", "product_id", "quantity", "created_by"])
    if error:
        return error

    order_date, error = parse_date(data.get("date") or date.today().isoformat(), "date")
    if error:
        return error

    customer_id, error = int_value(data["customer_id"], "customer_id")
    if error:
        return error

    product_id, error = int_value(data["product_id"], "product_id")
    if error:
        return error

    quantity, error = int_value(data["quantity"], "quantity")
    if error:
        return error

    customer = Customer.query.filter_by(customer_id=customer_id, is_deleted=False).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    product = _product_price(product_id, order_date)
    if not product:
        return jsonify({"error": "Price is not available for the selected product and date"}), 404

    discount_price, error = decimal_value(data.get("discount_price"), "discount_price")
    if error:
        return error

    total_amount = _calculate_total(product.price, discount_price, quantity)

    order = Order(
        customer_id=customer_id,
        product_id=product_id,
        date=order_date,
        price=product.price,
        quantity=quantity,
        discount_price=discount_price,
        remarks=data.get("remarks"),
        total_amount=total_amount,
        created_by=data["created_by"],
    )
    db.session.add(order)
    db.session.commit()
    return jsonify(order.as_dict()), 201


@orders_bp.route("/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data, error = request_data()
    if error:
        return error

    order_date, error = parse_date(data.get("date"), "date")
    if error:
        return error
    if order_date:
        order.date = order_date

    if "customer_id" in data:
        customer_id, error = int_value(data["customer_id"], "customer_id")
        if error:
            return error

        customer = Customer.query.filter_by(customer_id=customer_id, is_deleted=False).first()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        order.customer_id = customer_id

    if "product_id" in data or order_date:
        product_id, error = int_value(data.get("product_id", order.product_id), "product_id")
        if error:
            return error

        product = _product_price(product_id, order.date)
        if not product:
            return jsonify({"error": "Price is not available for the selected product and date"}), 404
        order.product_id = product_id
        order.price = product.price

    if "quantity" in data:
        order.quantity, error = int_value(data["quantity"], "quantity")
        if error:
            return error

    if "discount_price" in data:
        order.discount_price, error = decimal_value(data.get("discount_price"), "discount_price")
        if error:
            return error

    order.remarks = data.get("remarks", order.remarks)
    order.total_amount = _calculate_total(order.price, order.discount_price, order.quantity)
    mark_updated(order, data.get("updated_by"))
    db.session.commit()
    return jsonify(order.as_dict())


@orders_bp.route("/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.is_deleted = True
    mark_updated(order)
    db.session.commit()
    return jsonify({"message": "Order deleted"}), 200
