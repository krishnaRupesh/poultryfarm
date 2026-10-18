from pathlib import Path

from flasgger import Swagger
from flask import Flask, send_from_directory

from .config import Config
from .models import db
from .routes.customer_balances import customer_balances_bp
from .routes.customers import customers_bp
from .routes.incidents import incidents_bp
from .routes.orders import orders_bp
from .routes.payments import payments_bp
from .routes.products import products_bp
from .routes.feed_inventory import feed_inventory_bp
from .routes.daily_operations import daily_operations_bp
from .routes.cost_analysis import cost_analysis_bp
from .routes.flock_management import flock_management_bp


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    if app.config.get("AUTO_CREATE_TABLES"):
        with app.app_context():
            db.create_all()

    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(customers_bp, url_prefix="/api/customers")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(incidents_bp, url_prefix="/api/incidents")
    app.register_blueprint(customer_balances_bp, url_prefix="/api/customer-balances")
    app.register_blueprint(feed_inventory_bp, url_prefix="/api/feed")
    app.register_blueprint(daily_operations_bp, url_prefix="/api/daily")
    app.register_blueprint(cost_analysis_bp, url_prefix="/api/analysis")
    app.register_blueprint(flock_management_bp, url_prefix="/api/flock")

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Poultry Farm Management & Finance API",
            "description": "API documentation for feed inventory, daily operations, cost-per-egg analysis, orders, payments, products, customer balances, and flock/shed management.",
            "version": "2.1.0",
        },
        "tags": [
            {"name": "Flock & Shed Management", "description": "Manage poultry sheds and flock batches (e.g. 2026-march-a)"},
            {"name": "Feed Inventory", "description": "Manage poultry feed ingredients, stock levels, and valuations"},
            {"name": "Feed Purchases", "description": "Feed procurement, stock-in batches, and weighted average costing"},
            {"name": "Daily Operations", "description": "Daily live flock count, feeding consumption, and egg production/sales"},
            {"name": "Cost Analysis", "description": "Daily cost-per-bird, cost-per-egg, profit margins, and trends"},
            {"name": "Products", "description": "Product catalog and daily market rates"},
            {"name": "Customers", "description": "Customer profiles and contact info"},
            {"name": "Orders", "description": "Sales orders"},
            {"name": "Payments", "description": "Customer payment transactions"},
            {"name": "Customer Balances", "description": "Customer balance sheets and account ledgers"},
            {"name": "Incidents", "description": "Farm incident and expenditure tracking"},
        ],
    }
    Swagger(app, template=swagger_template)

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @app.route("/")
    def serve_dashboard():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:filename>")
    def serve_frontend_file(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    return app
