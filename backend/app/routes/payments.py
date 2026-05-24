from datetime import date

from flask import Blueprint, jsonify

from ..models import Customer, Payment, db
from .helpers import (
    active_query,
    decimal_value,
    int_value,
    mark_updated,
    parse_date,
    request_data,
    require_fields,
)


payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/", methods=["GET"])
def get_payments():
    payments = active_query(Payment).order_by(Payment.payment_date.desc(), Payment.payment_id.desc()).all()
    return jsonify([payment.as_dict() for payment in payments])


@payments_bp.route("/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return jsonify(payment.as_dict())


@payments_bp.route("/", methods=["POST"])
def add_payment():
    data, error = request_data()
    if error:
        return error

    error = require_fields(data, ["customer_id", "payment_amount", "created_by"])
    if error:
        return error

    customer_id, error = int_value(data["customer_id"], "customer_id")
    if error:
        return error

    customer = Customer.query.filter_by(customer_id=customer_id, is_deleted=False).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    payment_amount, error = decimal_value(data["payment_amount"], "payment_amount")
    if error:
        return error

    payment_date, error = parse_date(data.get("payment_date") or date.today().isoformat(), "payment_date")
    if error:
        return error

    payment = Payment(
        customer_id=customer_id,
        payment_amount=payment_amount,
        payment_date=payment_date,
        payment_mode=data.get("payment_mode"),
        remarks=data.get("remarks"),
        created_by=data["created_by"],
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify(payment.as_dict()), 201


@payments_bp.route("/<int:payment_id>", methods=["PUT"])
def update_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    data, error = request_data()
    if error:
        return error

    if "customer_id" in data:
        customer_id, error = int_value(data["customer_id"], "customer_id")
        if error:
            return error

        customer = Customer.query.filter_by(customer_id=customer_id, is_deleted=False).first()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        payment.customer_id = customer_id

    if "payment_amount" in data:
        payment.payment_amount, error = decimal_value(data["payment_amount"], "payment_amount")
        if error:
            return error

    payment_date, error = parse_date(data.get("payment_date"), "payment_date")
    if error:
        return error
    if payment_date:
        payment.payment_date = payment_date

    payment.payment_mode = data.get("payment_mode", payment.payment_mode)
    payment.remarks = data.get("remarks", payment.remarks)
    mark_updated(payment, data.get("updated_by"))
    db.session.commit()
    return jsonify(payment.as_dict())


@payments_bp.route("/<int:payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    payment.is_deleted = True
    mark_updated(payment)
    db.session.commit()
    return jsonify({"message": "Payment deleted"}), 200
