from flask import Blueprint, jsonify

from ..models import Incident, db
from .helpers import (
    active_query,
    decimal_value,
    mark_updated,
    parse_date,
    request_data,
    require_fields,
)


VALID_INCIDENT_TYPES = {"hens", "electric", "machinery", "others"}

incidents_bp = Blueprint("incidents", __name__)


def _validate_incident_type(value):
    if value not in VALID_INCIDENT_TYPES:
        return jsonify({
            "error": "incident_type must be one of hens, electric, machinery, others"
        }), 400
    return None


@incidents_bp.route("/", methods=["GET"])
def get_incidents():
    incidents = active_query(Incident).order_by(
        Incident.incident_date.desc(),
        Incident.incident_id.desc(),
    ).all()
    return jsonify([incident.as_dict() for incident in incidents])


@incidents_bp.route("/<int:incident_id>", methods=["GET"])
def get_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    return jsonify(incident.as_dict())


@incidents_bp.route("/", methods=["POST"])
def add_incident():
    data, error = request_data()
    if error:
        return error

    error = require_fields(data, ["name", "incident_type", "incident_date", "amount_spent", "created_by"])
    if error:
        return error

    error = _validate_incident_type(data["incident_type"])
    if error:
        return error

    incident_date, error = parse_date(data["incident_date"], "incident_date")
    if error:
        return error

    amount_spent, error = decimal_value(data["amount_spent"], "amount_spent")
    if error:
        return error

    incident = Incident(
        name=data["name"],
        incident_type=data["incident_type"],
        incident_date=incident_date,
        summary=data.get("summary"),
        amount_spent=amount_spent,
        created_by=data["created_by"],
    )
    db.session.add(incident)
    db.session.commit()
    return jsonify(incident.as_dict()), 201


@incidents_bp.route("/<int:incident_id>", methods=["PUT"])
def update_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data, error = request_data()
    if error:
        return error

    if "incident_type" in data:
        error = _validate_incident_type(data["incident_type"])
        if error:
            return error
        incident.incident_type = data["incident_type"]

    incident_date, error = parse_date(data.get("incident_date"), "incident_date")
    if error:
        return error
    if incident_date:
        incident.incident_date = incident_date

    if "amount_spent" in data:
        incident.amount_spent, error = decimal_value(data["amount_spent"], "amount_spent")
        if error:
            return error

    incident.name = data.get("name", incident.name)
    incident.summary = data.get("summary", incident.summary)
    mark_updated(incident, data.get("updated_by"))
    db.session.commit()
    return jsonify(incident.as_dict())


@incidents_bp.route("/<int:incident_id>", methods=["DELETE"])
def delete_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    incident.is_deleted = True
    mark_updated(incident)
    db.session.commit()
    return jsonify({"message": "Incident deleted"}), 200
