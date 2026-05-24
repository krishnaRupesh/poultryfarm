from datetime import datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request

from ..models import Customer, CustomerBalanceSummary, Order, Payment, db
from .helpers import int_value, request_data


customer_balances_bp = Blueprint("customer_balances", __name__)


def _remaining_balance(customer_id):
    order_total = sum(
        (order.total_amount or Decimal("0"))
        for order in Order.query.filter_by(customer_id=customer_id, is_deleted=False).all()
    )
    payment_total = sum(
        (payment.payment_amount or Decimal("0"))
        for payment in Payment.query.filter_by(customer_id=customer_id, is_deleted=False).all()
    )
    return order_total - payment_total


def _refresh_customer_balance(customer, updated_by):
    now = datetime.utcnow()
    summary = CustomerBalanceSummary.query.get(customer.customer_id)
    if not summary:
        summary = CustomerBalanceSummary(
            customer_id=customer.customer_id,
            remaining_balance=Decimal("0"),
            created_by=updated_by,
        )
        db.session.add(summary)

    summary.remaining_balance = _remaining_balance(customer.customer_id)
    summary.last_updated = now
    summary.updated_at = now
    summary.updated_by = updated_by
    summary.is_deleted = False
    return summary


@customer_balances_bp.route("/summary", methods=["GET"])
def get_balance_summary():
    summaries = CustomerBalanceSummary.query.filter_by(is_deleted=False).order_by(
        CustomerBalanceSummary.remaining_balance.desc()
    ).all()
    return jsonify([summary.as_dict() for summary in summaries])


@customer_balances_bp.route("/refresh", methods=["POST"])
def refresh_balance_summary():
    data, _ = request_data()
    updated_by = (data or {}).get("updated_by", "system")
    customers = Customer.query.filter_by(is_deleted=False).all()
    summaries = [_refresh_customer_balance(customer, updated_by) for customer in customers]
    db.session.commit()
    summaries.sort(key=lambda summary: summary.remaining_balance, reverse=True)
    return jsonify([summary.as_dict() for summary in summaries])


@customer_balances_bp.route("/<int:customer_id>/details", methods=["GET"])
def get_balance_details(customer_id):
    return _balance_details_response(customer_id)


@customer_balances_bp.route("/details", methods=["GET"])
def get_balance_details_by_query():
    customer_id = request.args.get("customer_id")
    customer_name = request.args.get("customer_name")

    if customer_id:
        customer_id, error = int_value(customer_id, "customer_id")
        if error:
            return error
        return _balance_details_response(customer_id)
    if customer_name:
        customer = Customer.query.filter_by(customer_name=customer_name, is_deleted=False).first_or_404()
        return _balance_details_response(customer.customer_id)

    return jsonify({"error": "customer_id or customer_name is required"}), 400


def _balance_details_response(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id, is_deleted=False).first_or_404()
    summary = CustomerBalanceSummary.query.get(customer_id)
    if not summary:
        summary = _refresh_customer_balance(customer, "system")
        db.session.commit()

    rows = []
    for order in Order.query.filter_by(customer_id=customer_id, is_deleted=False).all():
        rows.append({
            "date": order.date.isoformat(),
            "id": order.order_id,
            "quantity": order.quantity,
            "amount": float(order.total_amount),
            "type": "order",
        })

    for payment in Payment.query.filter_by(customer_id=customer_id, is_deleted=False).all():
        rows.append({
            "date": payment.payment_date.isoformat(),
            "id": payment.payment_id,
            "quantity": None,
            "amount": float(payment.payment_amount),
            "type": "payment",
        })

    rows.sort(key=lambda row: row["date"], reverse=True)
    return jsonify({
        "customer_id": customer.customer_id,
        "customer_name": customer.customer_name,
        "remaining_balance": float(summary.remaining_balance),
        "details": rows,
    })
