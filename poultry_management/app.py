from flask import Flask
from flasgger import Swagger
from config import Config
from models import db
from routes.products import products_bp
# from routes.customers import customers_bp
# from routes.orders import orders_bp
# from routes.payments import payments_bp
# from routes.incidents import incidents_bp
# from routes.customer_balance import customer_balance_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Initialize Swagger
swagger = Swagger(app)

# Register Blueprints
app.register_blueprint(products_bp, url_prefix='/api/products')
# app.register_blueprint(customers_bp, url_prefix='/api/customers')
# app.register_blueprint(orders_bp, url_prefix='/api/orders')
# app.register_blueprint(payments_bp, url_prefix='/api/payments')
# app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
# app.register_blueprint(customer_balance_bp, url_prefix='/api/customer_balance')

if __name__ == "__main__":
    app.run(debug=True)
