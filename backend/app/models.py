from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(255), nullable=False)
    updated_by = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean, default=False)

    def as_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": float(self.price),
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }

# Define other models similarly for Customers, Orders, Payments, Incidents, CustomerBalanceSummary

