from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _date_or_none(value):
    return value.isoformat() if value else None


def _datetime_or_none(value):
    return value.isoformat() if value else None


def _money_or_none(value):
    return float(value) if value is not None else None


class AuditMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(255), nullable=False)
    updated_by = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean, default=False)


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
            "price": _money_or_none(self.price),
            "date": _date_or_none(self.date),
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


class Customer(db.Model, AuditMixin):
    __tablename__ = "customers"

    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    email_id = db.Column(db.String(255))

    orders = db.relationship("Order", back_populates="customer")
    payments = db.relationship("Payment", back_populates="customer")
    balance_summary = db.relationship(
        "CustomerBalanceSummary",
        back_populates="customer",
        uselist=False,
    )

    def as_dict(self):
        return {
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "phone_number": self.phone_number,
            "address": self.address,
            "email_id": self.email_id,
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


class Order(db.Model, AuditMixin):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    discount_price = db.Column(db.Numeric(10, 2))
    remarks = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    customer = db.relationship("Customer", back_populates="orders")
    product = db.relationship("Product")

    def as_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.customer_name if self.customer else None,
            "product_id": self.product_id,
            "product_name": self.product.product_name if self.product else None,
            "date": _date_or_none(self.date),
            "price": _money_or_none(self.price),
            "quantity": self.quantity,
            "discount_price": _money_or_none(self.discount_price),
            "remarks": self.remarks,
            "total_amount": _money_or_none(self.total_amount),
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


class Payment(db.Model, AuditMixin):
    __tablename__ = "payments"

    payment_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    payment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_mode = db.Column(db.String(50))
    remarks = db.Column(db.Text)

    customer = db.relationship("Customer", back_populates="payments")

    def as_dict(self):
        return {
            "payment_id": self.payment_id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.customer_name if self.customer else None,
            "payment_amount": _money_or_none(self.payment_amount),
            "payment_date": _date_or_none(self.payment_date),
            "payment_mode": self.payment_mode,
            "remarks": self.remarks,
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


class Incident(db.Model, AuditMixin):
    __tablename__ = "incidents"

    incident_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)
    incident_date = db.Column(db.Date, nullable=False)
    summary = db.Column(db.Text)
    amount_spent = db.Column(db.Numeric(10, 2), nullable=False)

    def as_dict(self):
        return {
            "incident_id": self.incident_id,
            "name": self.name,
            "incident_type": self.incident_type,
            "incident_date": _date_or_none(self.incident_date),
            "summary": self.summary,
            "amount_spent": _money_or_none(self.amount_spent),
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


class CustomerBalanceSummary(db.Model, AuditMixin):
    __tablename__ = "customer_balance_summary"

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), primary_key=True)
    remaining_balance = db.Column(db.Numeric(10, 2), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    customer = db.relationship("Customer", back_populates="balance_summary")

    def as_dict(self):
        return {
            "customer_id": self.customer_id,
            "customer_name": self.customer.customer_name if self.customer else None,
            "remaining_balance": _money_or_none(self.remaining_balance),
            "last_updated": _datetime_or_none(self.last_updated),
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }

