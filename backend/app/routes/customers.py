from flask import Blueprint, jsonify

from ..models import Customer, db
from .helpers import active_query, mark_updated, request_data, require_fields


customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/", methods=["GET"])
def get_customers():
    """
    List customers
    ---
    tags:
      - Customers
    parameters:
      - in: query
        name: include_deleted
        type: boolean
        required: false
    responses:
      200:
        description: Customer list
    """
    customers = active_query(Customer).order_by(Customer.customer_name.asc()).all()
    return jsonify([customer.as_dict() for customer in customers])


@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    """
    Get a customer
    ---
    tags:
      - Customers
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
    responses:
      200:
        description: Customer details
      404:
        description: Customer not found
    """
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.as_dict())


@customers_bp.route("/", methods=["POST"])
def add_customer():
    """
    Create a customer
    ---
    tags:
      - Customers
    parameters:
      - in: body
        name: customer
        required: true
        schema:
          type: object
          required:
            - customer_name
            - phone_number
            - address
            - created_by
          properties:
            customer_name:
              type: string
            phone_number:
              type: string
            address:
              type: string
            email_id:
              type: string
            created_by:
              type: string
    responses:
      201:
        description: Customer created
    """
    data, error = request_data()
    if error:
        return error

    error = require_fields(data, ["customer_name", "phone_number", "address", "created_by"])
    if error:
        return error

    customer = Customer(
        customer_name=data["customer_name"],
        phone_number=data["phone_number"],
        address=data["address"],
        email_id=data.get("email_id"),
        created_by=data["created_by"],
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.as_dict()), 201


@customers_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    """
    Update a customer
    ---
    tags:
      - Customers
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
      - in: body
        name: customer
        schema:
          type: object
          properties:
            customer_name:
              type: string
            phone_number:
              type: string
            address:
              type: string
            email_id:
              type: string
            updated_by:
              type: string
    responses:
      200:
        description: Customer updated
    """
    customer = Customer.query.get_or_404(customer_id)
    data, error = request_data()
    if error:
        return error

    customer.customer_name = data.get("customer_name", customer.customer_name)
    customer.phone_number = data.get("phone_number", customer.phone_number)
    customer.address = data.get("address", customer.address)
    customer.email_id = data.get("email_id", customer.email_id)
    mark_updated(customer, data.get("updated_by"))
    db.session.commit()
    return jsonify(customer.as_dict())


@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    """
    Soft delete a customer
    ---
    tags:
      - Customers
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
    responses:
      200:
        description: Customer deleted
    """
    customer = Customer.query.get_or_404(customer_id)
    customer.is_deleted = True
    mark_updated(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted"}), 200
