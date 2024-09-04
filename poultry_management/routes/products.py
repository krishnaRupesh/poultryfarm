from flask import Blueprint, jsonify, request
from models import db, Product
from datetime import datetime

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.as_dict() for product in products])

@products_bp.route('/', methods=['POST'])
def add_product():
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
    product = Product.query.get_or_404(id)
    product.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200

