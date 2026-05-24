from flask import Blueprint, jsonify, request

from ..models import db, Product
from .helpers import active_query, int_value, mark_updated, parse_date, request_data, require_fields

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    """
    Get a list of all products
    ---
    responses:
      200:
        description: A list of products
        schema:
          type: array
          items:
            type: object
            properties:
              product_id:
                type: integer
                description: The product ID
              product_name:
                type: string
                description: The name of the product
              price:
                type: number
                format: float
                description: The price of the product
              date:
                type: string
                format: date
                description: The date when the price is applicable
    """
    products = active_query(Product).order_by(Product.date.desc(), Product.product_name.asc()).all()
    return jsonify([product.as_dict() for product in products])


@products_bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.as_dict())


@products_bp.route('/price', methods=['GET'])
def get_product_price():
    product_id = request.args.get('product_id')
    product_name = request.args.get('product_name')
    requested_date, error = parse_date(request.args.get('date'), 'date')
    if error:
        return error

    if not requested_date or not (product_id or product_name):
        return jsonify({'error': 'product_id or product_name and date are required'}), 400

    query = Product.query.filter_by(date=requested_date, is_deleted=False)
    if product_id:
        product_id, error = int_value(product_id, 'product_id')
        if error:
            return error
        query = query.filter_by(product_id=product_id)
    else:
        query = query.filter_by(product_name=product_name)

    product = query.first()
    if not product:
        return jsonify({'error': 'Price is not available for the selected product and date'}), 404

    return jsonify(product.as_dict())

@products_bp.route('/', methods=['POST'])
def add_product():
    """
    Add a new product
    ---
    parameters:
      - in: body
        name: product
        description: The product to create
        schema:
          type: object
          required:
            - product_name
            - price
            - date
          properties:
            product_name:
              type: string
            price:
              type: number
              format: float
            date:
              type: string
              format: date
            created_by:
              type: string
    responses:
      201:
        description: Product created successfully
        schema:
          type: object
          properties:
            product_id:
              type: integer
            product_name:
              type: string
            price:
              type: number
              format: float
            date:
              type: string
              format: date
    """
    data, error = request_data()
    if error:
        return error

    error = require_fields(data, ['product_name', 'price', 'date', 'created_by'])
    if error:
        return error

    product_date, error = parse_date(data.get('date'), 'date')
    if error:
        return error

    new_product = Product(
        product_name=data['product_name'],
        price=data['price'],
        date=product_date,
        created_by=data['created_by']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.as_dict()), 201

@products_bp.route('/<int:id>', methods=['PUT'])
def update_product(id):
    """
    Update an existing product
    ---
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The product ID
      - in: body
        name: product
        description: The product data to update
        schema:
          type: object
          properties:
            product_name:
              type: string
            price:
              type: number
              format: float
            date:
              type: string
              format: date
            updated_by:
              type: string
    responses:
      200:
        description: Product updated successfully
        schema:
          type: object
          properties:
            product_id:
              type: integer
            product_name:
              type: string
            price:
              type: number
              format: float
            date:
              type: string
              format: date
    """
    product = Product.query.get_or_404(id)
    data, error = request_data()
    if error:
        return error

    product_date, error = parse_date(data.get('date'), 'date')
    if error:
        return error

    product.product_name = data.get('product_name', product.product_name)
    product.price = data.get('price', product.price)
    product.date = product_date or product.date
    mark_updated(product, data.get('updated_by'))
    db.session.commit()
    return jsonify(product.as_dict())

@products_bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    """
    Soft delete a product
    ---
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The product ID
    responses:
      200:
        description: Product deleted successfully
    """
    product = Product.query.get_or_404(id)
    product.is_deleted = True
    mark_updated(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200

