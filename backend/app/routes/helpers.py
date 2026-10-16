from datetime import date, datetime
from decimal import Decimal

from flask import jsonify, request


def request_data():
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"error": "Request body must be valid JSON"}), 400)
    return data, None


def require_fields(data, fields):
    missing = [field for field in fields if data.get(field) in (None, "")]
    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400
    return None


def parse_date(value, field_name):
    if value in (None, ""):
        return None, None
    if isinstance(value, date):
        return value, None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), None
    except (TypeError, ValueError):
        return None, (jsonify({"error": f"{field_name} must use YYYY-MM-DD format"}), 400)


def decimal_value(value, field_name):
    if value in (None, ""):
        return None, None
    try:
        return Decimal(str(value)), None
    except Exception:
        return None, (jsonify({"error": f"{field_name} must be a valid number"}), 400)


def int_value(value, field_name):
    try:
        return int(value), None
    except (TypeError, ValueError):
        return None, (jsonify({"error": f"{field_name} must be a valid integer"}), 400)


def active_query(model):
    query = model.query
    if request.args.get("include_deleted", "").lower() != "true":
        query = query.filter_by(is_deleted=False)
    return query


def mark_updated(record, updated_by=None):
    record.updated_at = datetime.utcnow()
    if updated_by is not None:
        record.updated_by = updated_by
