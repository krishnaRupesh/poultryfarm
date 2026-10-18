from datetime import date, datetime
from flask import Blueprint, jsonify, request

from ..models import Shed, FlockBatch
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
    int_value,
    parse_date,
    request_data,
    require_fields,
)

flock_management_bp = Blueprint("flock_management", __name__)


# -----------------------------------------------------------------------------
# SHEDS CRUD
# -----------------------------------------------------------------------------
@flock_management_bp.route("/sheds", methods=["GET"])
def get_sheds():
    """
    List all poultry sheds
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: query
        name: status
        type: string
        description: Filter by status (e.g. Active, Maintenance, Empty)
      - in: query
        name: include_deleted
        type: boolean
        description: Include soft-deleted sheds
    responses:
      200:
        description: List of sheds
    """
    status_filter = request.args.get("status")
    filters = {"status": status_filter} if status_filter else None
    sheds = list_records(
        table_name="sheds",
        model_class=Shed,
        filters=filters,
        order_by="shed_name ASC",
        default_order=Shed.shed_name.asc(),
    )
    return jsonify(sheds)


@flock_management_bp.route("/sheds/<int:shed_id>", methods=["GET"])
def get_shed(shed_id):
    """
    Get shed details
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: path
        name: shed_id
        type: integer
        required: true
    responses:
      200:
        description: Shed details
      404:
        description: Shed not found
    """
    shed = get_record("sheds", Shed, "shed_id", shed_id)
    if not shed:
        return jsonify({"error": "Shed not found"}), 404
    return jsonify(shed)


@flock_management_bp.route("/sheds", methods=["POST"])
def create_shed():
    """
    Create a new poultry shed
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - shed_name
          properties:
            shed_name:
              type: string
              example: "Shed A"
            capacity:
              type: integer
              example: 10000
            shed_type:
              type: string
              example: "Layer"
            status:
              type: string
              example: "Active"
            location:
              type: string
              example: "North Wing"
            description:
              type: string
            created_by:
              type: string
    responses:
      201:
        description: Shed created
    """
    data, err = request_data()
    if err:
        return err
    err = require_fields(data, ["shed_name"])
    if err:
        return err

    shed_name = data["shed_name"].strip()
    capacity = int(data.get("capacity", 10000))
    shed_type = (data.get("shed_type") or "Layer").strip()
    status = (data.get("status") or "Active").strip()
    created_by = (data.get("created_by") or "system").strip()

    row_data = {
        "shed_name": shed_name,
        "capacity": capacity,
        "shed_type": shed_type,
        "status": status,
        "location": data.get("location"),
        "description": data.get("description"),
        "created_by": created_by,
        "updated_by": created_by,
    }
    created = create_record("sheds", Shed, "shed_id", row_data)
    return jsonify(created), 201


@flock_management_bp.route("/sheds/<int:shed_id>", methods=["PUT"])
def update_shed(shed_id):
    """
    Update shed details
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: path
        name: shed_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
    responses:
      200:
        description: Shed updated
      404:
        description: Shed not found
    """
    data, err = request_data()
    if err:
        return err

    updates = {}
    if "shed_name" in data and data["shed_name"]:
        updates["shed_name"] = data["shed_name"].strip()
    if "capacity" in data:
        updates["capacity"] = int(data["capacity"])
    if "shed_type" in data:
        updates["shed_type"] = data["shed_type"].strip()
    if "status" in data:
        updates["status"] = data["status"].strip()
    if "location" in data:
        updates["location"] = data["location"]
    if "description" in data:
        updates["description"] = data["description"]
    if "updated_by" in data:
        updates["updated_by"] = data["updated_by"]

    updated = update_record("sheds", Shed, "shed_id", shed_id, updates)
    if not updated:
        return jsonify({"error": "Shed not found"}), 404
    return jsonify(updated)


@flock_management_bp.route("/sheds/<int:shed_id>", methods=["DELETE"])
def delete_shed(shed_id):
    """
    Soft-delete a shed
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: path
        name: shed_id
        type: integer
        required: true
    responses:
      200:
        description: Shed soft-deleted
    """
    deleted_by = request.args.get("deleted_by", "system")
    success = soft_delete_record("sheds", Shed, "shed_id", shed_id, deleted_by)
    if not success:
        return jsonify({"error": "Shed not found"}), 404
    return jsonify({"message": "Shed archived successfully", "shed_id": shed_id})


@flock_management_bp.route("/sheds/<int:shed_id>/restore", methods=["POST"])
def restore_shed_endpoint(shed_id):
    """
    Restore an archived shed
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: path
        name: shed_id
        type: integer
        required: true
    responses:
      200:
        description: Shed restored
    """
    restored = restore_record("sheds", Shed, "shed_id", shed_id)
    if not restored:
        return jsonify({"error": "Shed not found"}), 404
    return jsonify({"message": "Shed restored successfully", "shed": restored})


# -----------------------------------------------------------------------------
# FLOCK BATCHES CRUD
# -----------------------------------------------------------------------------
@flock_management_bp.route("/batches", methods=["GET"])
def get_batches():
    """
    List flock batches
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: query
        name: status
        type: string
        description: Filter by status (Active, Culled, Completed)
      - in: query
        name: shed_id
        type: integer
      - in: query
        name: include_deleted
        type: boolean
    responses:
      200:
        description: List of flock batches
    """
    filters = {}
    if request.args.get("status"):
        filters["status"] = request.args.get("status")
    if request.args.get("shed_id"):
        filters["shed_id"] = int(request.args.get("shed_id"))

    batches = list_records(
        table_name="flock_batches",
        model_class=FlockBatch,
        filters=filters if filters else None,
        order_by="placement_date DESC",
        default_order=FlockBatch.placement_date.desc(),
    )
    return jsonify(batches)


@flock_management_bp.route("/batches/<int:batch_id>", methods=["GET"])
def get_batch(batch_id):
    """
    Get flock batch details
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: path
        name: batch_id
        type: integer
        required: true
    responses:
      200:
        description: Batch details
      404:
        description: Batch not found
    """
    batch = get_record("flock_batches", FlockBatch, "batch_id", batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404
    return jsonify(batch)


@flock_management_bp.route("/batches", methods=["POST"])
def create_batch():
    """
    Create a new flock batch placed in a shed
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - batch_name
            - placement_date
            - initial_birds
          properties:
            batch_name:
              type: string
              example: "2026-march-a"
            shed_id:
              type: integer
              example: 1
            breed:
              type: string
              example: "Layer (BV300)"
            placement_date:
              type: string
              format: date
              example: "2026-03-01"
            initial_birds:
              type: integer
              example: 10000
            initial_age_weeks:
              type: integer
              example: 18
            remarks:
              type: string
    responses:
      201:
        description: Batch created
    """
    data, err = request_data()
    if err:
        return err
    err = require_fields(data, ["batch_name", "placement_date", "initial_birds"])
    if err:
        return err

    p_date, err = parse_date(data["placement_date"], "placement_date")
    if err:
        return err

    initial_birds, err = int_value(data["initial_birds"], "initial_birds")
    if err or initial_birds <= 0:
        return jsonify({"error": "initial_birds must be a positive integer"}), 400

    current_birds = int(data.get("current_birds", initial_birds))
    initial_age = int(data.get("initial_age_weeks", 18))
    created_by = (data.get("created_by") or "system").strip()

    row_data = {
        "batch_name": data["batch_name"].strip(),
        "shed_id": int(data["shed_id"]) if data.get("shed_id") else None,
        "breed": (data.get("breed") or "Layer (BV300)").strip(),
        "bird_type": (data.get("bird_type") or "Layer").strip(),
        "placement_date": p_date,
        "initial_birds": initial_birds,
        "current_birds": current_birds,
        "initial_age_weeks": initial_age,
        "status": (data.get("status") or "Active").strip(),
        "remarks": data.get("remarks"),
        "created_by": created_by,
        "updated_by": created_by,
    }
    created = create_record("flock_batches", FlockBatch, "batch_id", row_data)
    return jsonify(created), 201


@flock_management_bp.route("/batches/<int:batch_id>", methods=["PUT"])
def update_batch(batch_id):
    """
    Update flock batch details
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: path
        name: batch_id
        type: integer
        required: true
    responses:
      200:
        description: Batch updated
      404:
        description: Batch not found
    """
    data, err = request_data()
    if err:
        return err

    updates = {}
    if "batch_name" in data and data["batch_name"]:
        updates["batch_name"] = data["batch_name"].strip()
    if "shed_id" in data:
        updates["shed_id"] = int(data["shed_id"]) if data["shed_id"] else None
    if "breed" in data:
        updates["breed"] = data["breed"].strip()
    if "current_birds" in data:
        updates["current_birds"] = int(data["current_birds"])
    if "status" in data:
        updates["status"] = data["status"].strip()
    if "depletion_date" in data:
        d, err = parse_date(data["depletion_date"], "depletion_date")
        if not err:
            updates["depletion_date"] = d
    if "remarks" in data:
        updates["remarks"] = data["remarks"]
    if "updated_by" in data:
        updates["updated_by"] = data["updated_by"]

    updated = update_record("flock_batches", FlockBatch, "batch_id", batch_id, updates)
    if not updated:
        return jsonify({"error": "Batch not found"}), 404
    return jsonify(updated)


@flock_management_bp.route("/batches/<int:batch_id>", methods=["DELETE"])
def delete_batch(batch_id):
    """
    Soft-delete a flock batch
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: path
        name: batch_id
        type: integer
        required: true
    responses:
      200:
        description: Batch soft-deleted
    """
    deleted_by = request.args.get("deleted_by", "system")
    success = soft_delete_record("flock_batches", FlockBatch, "batch_id", batch_id, deleted_by)
    if not success:
        return jsonify({"error": "Batch not found"}), 404
    return jsonify({"message": "Batch archived successfully", "batch_id": batch_id})


@flock_management_bp.route("/batches/<int:batch_id>/restore", methods=["POST"])
def restore_batch_endpoint(batch_id):
    """
    Restore an archived flock batch
    ---
    tags:
      - Flock & Shed Management
    parameters:
      - in: path
        name: batch_id
        type: integer
        required: true
    responses:
      200:
        description: Batch restored
    """
    restored = restore_record("flock_batches", FlockBatch, "batch_id", batch_id)
    if not restored:
        return jsonify({"error": "Batch not found"}), 404
    return jsonify({"message": "Batch restored successfully", "batch": restored})
