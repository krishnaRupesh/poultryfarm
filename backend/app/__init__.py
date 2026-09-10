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


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Swagger(app)

    if app.config.get("AUTO_CREATE_TABLES"):
        with app.app_context():
            db.create_all()

    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(customers_bp, url_prefix="/api/customers")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(incidents_bp, url_prefix="/api/incidents")
    app.register_blueprint(customer_balances_bp, url_prefix="/api/customer-balances")

    @app.route("/")
    def serve_dashboard():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:filename>")
    def serve_frontend_file(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    return app
