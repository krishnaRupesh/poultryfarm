from flask import Blueprint, jsonify, request
from models import db, Product
from datetime import datetime

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
    products = Product.query.all()
    return jsonify([product.as_dict() for product in products])

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
    data = request.json
    new_product = Product(
        product_name=data['product_name'],
        price=data['price'],
        date=data['date'],
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
    data = request.json
    product.product_name = data.get('product_name', product.product_name)
    product.price = data.get('price', product.price)
    product.date = data.get('date', product.date)
    product.updated_by = data['updated_by']
    product.updated_at = datetime.utcnow()
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
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200

