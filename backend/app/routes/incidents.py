from flask import Blueprint, jsonify, request

from ..models import Incident, Shed, FlockBatch, db
from ..data_layer import (
    list_records,
    get_record,
    create_record,
    update_record,
    soft_delete_record,
    restore_record,
    is_bigquery,
)
from .helpers import (
    decimal_value,
    int_value,
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
    """
    List incidents with optional shed/batch filtering and archive view
    ---
    tags:
      - Incidents
    parameters:
      - in: query
        name: include_deleted
        type: boolean
        required: false
      - in: query
        name: deleted_only
        type: boolean
        required: false
      - in: query
        name: shed_id
        type: integer
        required: false
      - in: query
        name: batch_id
        type: integer
        required: false
      - in: query
        name: incident_type
        type: string
        required: false
    responses:
      200:
        description: Incident list ordered by incident date descending
    """
    filters = {}
    if request.args.get("shed_id"):
        filters["shed_id"] = int(request.args.get("shed_id"))
    if request.args.get("batch_id"):
        filters["batch_id"] = int(request.args.get("batch_id"))
    if request.args.get("incident_type"):
        filters["incident_type"] = request.args.get("incident_type")

    incidents = list_records(
        table_name="incidents",
        model_class=Incident,
        filters=filters if filters else None,
        order_by="incident_date DESC, incident_id DESC",
        default_order=Incident.incident_date.desc(),
    )
    return jsonify(incidents)


@incidents_bp.route("/<int:incident_id>", methods=["GET"])
def get_incident(incident_id):
    """
    Get an incident
    ---
    tags:
      - Incidents
    parameters:
      - in: path
        name: incident_id
        type: integer
        required: true
    responses:
      200:
        description: Incident details
      404:
        description: Incident not found
    """
    incident = get_record("incidents", Incident, "incident_id", incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404
    return jsonify(incident)


@incidents_bp.route("/", methods=["POST"])
def add_incident():
    """
    Create an incident with optional Shed and Batch attribution
    ---
    tags:
      - Incidents
    parameters:
      - in: body
        name: incident
        required: true
        schema:
          type: object
          required:
            - name
            - incident_type
            - incident_date
            - amount_spent
            - created_by
          properties:
            name:
              type: string
            incident_type:
              type: string
              enum: [hens, electric, machinery, others]
            incident_date:
              type: string
              format: date
            summary:
              type: string
            amount_spent:
              type: number
            shed_id:
              type: integer
              description: Optional affected shed ID
            batch_id:
              type: integer
              description: Optional affected flock batch ID
            created_by:
              type: string
    responses:
      201:
        description: Incident created
    """
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

    shed_id = int(data["shed_id"]) if data.get("shed_id") else None
    batch_id = int(data["batch_id"]) if data.get("batch_id") else None
    created_by = (data.get("created_by") or "system").strip()

    row_data = {
        "name": data["name"].strip(),
        "incident_type": data["incident_type"],
        "incident_date": incident_date,
        "summary": data.get("summary"),
        "amount_spent": amount_spent,
        "shed_id": shed_id,
        "batch_id": batch_id,
        "created_by": created_by,
        "updated_by": created_by,
    }

    created = create_record("incidents", Incident, "incident_id", row_data)
    return jsonify(created), 201


@incidents_bp.route("/<int:incident_id>", methods=["PUT"])
def update_incident(incident_id):
    """
    Update an incident
    ---
    tags:
      - Incidents
    parameters:
      - in: path
        name: incident_id
        type: integer
        required: true
      - in: body
        name: incident
        schema:
          type: object
    responses:
      200:
        description: Incident updated
      404:
        description: Incident not found
    """
    data, error = request_data()
    if error:
        return error

    updates = {}
    if "incident_type" in data:
        error = _validate_incident_type(data["incident_type"])
        if error:
            return error
        updates["incident_type"] = data["incident_type"]

    if "incident_date" in data:
        incident_date, error = parse_date(data.get("incident_date"), "incident_date")
        if error:
            return error
        if incident_date:
            updates["incident_date"] = incident_date

    if "amount_spent" in data:
        amount_spent, error = decimal_value(data["amount_spent"], "amount_spent")
        if error:
            return error
        updates["amount_spent"] = amount_spent

    if "name" in data:
        updates["name"] = data["name"].strip()
    if "summary" in data:
        updates["summary"] = data["summary"]
    if "shed_id" in data:
        updates["shed_id"] = int(data["shed_id"]) if data["shed_id"] else None
    if "batch_id" in data:
        updates["batch_id"] = int(data["batch_id"]) if data["batch_id"] else None
    if "updated_by" in data:
        updates["updated_by"] = data["updated_by"]

    updated = update_record("incidents", Incident, "incident_id", incident_id, updates)
    if not updated:
        return jsonify({"error": "Incident not found"}), 404
    return jsonify(updated)


@incidents_bp.route("/<int:incident_id>", methods=["DELETE"])
def delete_incident(incident_id):
    """
    Soft delete an incident
    ---
    tags:
      - Incidents
    parameters:
      - in: path
        name: incident_id
        type: integer
        required: true
    responses:
      200:
        description: Incident soft-deleted
    """
    deleted_by = request.args.get("deleted_by", "system")
    success = soft_delete_record("incidents", Incident, "incident_id", incident_id, deleted_by)
    if not success:
        return jsonify({"error": "Incident not found"}), 404
    return jsonify({"message": "Incident archived successfully", "incident_id": incident_id}), 200


@incidents_bp.route("/<int:incident_id>/restore", methods=["POST"])
def restore_incident(incident_id):
    """
    Restore an archived incident
    ---
    tags:
      - Incidents
    parameters:
      - in: path
        name: incident_id
        type: integer
        required: true
    responses:
      200:
        description: Incident restored
      404:
        description: Incident not found
    """
    restored = restore_record("incidents", Incident, "incident_id", incident_id)
    if not restored:
        return jsonify({"error": "Incident not found"}), 404
    return jsonify({"message": "Incident restored successfully", "incident": restored}), 200
