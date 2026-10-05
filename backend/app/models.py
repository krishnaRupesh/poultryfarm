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


class FeedItem(db.Model, AuditMixin):
    __tablename__ = "feed_items"

    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    category = db.Column(db.String(100))
    default_unit = db.Column(db.String(20), default="kg")
    current_stock_kg = db.Column(db.Numeric(12, 2), default=0.0)
    average_cost_per_kg = db.Column(db.Numeric(10, 4), default=0.0)
    reorder_level_kg = db.Column(db.Numeric(10, 2), default=100.0)

    purchases = db.relationship("FeedPurchase", back_populates="item", cascade="all, delete-orphan")
    consumptions = db.relationship("DailyFeedConsumption", back_populates="item")

    def as_dict(self):
        stock_kg = float(self.current_stock_kg or 0.0)
        stock_mt = round(stock_kg / 1000.0, 3)
        avg_cost = float(self.average_cost_per_kg or 0.0)
        reorder_kg = float(self.reorder_level_kg or 100.0)
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category,
            "default_unit": self.default_unit,
            "current_stock_kg": stock_kg,
            "current_stock_mt": stock_mt,
            "average_cost_per_kg": avg_cost,
            "average_cost_per_mt": round(avg_cost * 1000.0, 2),
            "reorder_level_kg": reorder_kg,
            "total_valuation": round(stock_kg * avg_cost, 2),
            "is_low_stock": stock_kg <= reorder_kg,
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


class FeedPurchase(db.Model, AuditMixin):
    __tablename__ = "feed_purchases"

    purchase_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("feed_items.item_id"), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    quantity_kg = db.Column(db.Numeric(12, 2), nullable=False)
    cost_per_kg = db.Column(db.Numeric(10, 4), nullable=False)
    total_cost = db.Column(db.Numeric(12, 2), nullable=False)
    vendor_name = db.Column(db.String(255))
    invoice_no = db.Column(db.String(100))
    remarks = db.Column(db.Text)

    item = db.relationship("FeedItem", back_populates="purchases")

    def as_dict(self):
        qty_kg = float(self.quantity_kg or 0.0)
        c_kg = float(self.cost_per_kg or 0.0)
        return {
            "purchase_id": self.purchase_id,
            "item_id": self.item_id,
            "item_name": self.item.name if self.item else None,
            "purchase_date": _date_or_none(self.purchase_date),
            "quantity_kg": qty_kg,
            "quantity_mt": round(qty_kg / 1000.0, 3),
            "cost_per_kg": c_kg,
            "cost_per_mt": round(c_kg * 1000.0, 2),
            "total_cost": _money_or_none(self.total_cost),
            "vendor_name": self.vendor_name,
            "invoice_no": self.invoice_no,
            "remarks": self.remarks,
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


class DailyFlockStatus(db.Model, AuditMixin):
    __tablename__ = "daily_flock_status"

    status_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    active_birds = db.Column(db.Integer, nullable=False)
    mortality = db.Column(db.Integer, default=0)
    remarks = db.Column(db.Text)

    def as_dict(self):
        return {
            "status_id": self.status_id,
            "date": _date_or_none(self.date),
            "active_birds": self.active_birds,
            "mortality": self.mortality or 0,
            "remarks": self.remarks,
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


class DailyFeedConsumption(db.Model, AuditMixin):
    __tablename__ = "daily_feed_consumption"

    consumption_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("feed_items.item_id"), nullable=False)
    quantity_kg = db.Column(db.Numeric(12, 2), nullable=False)
    cost_per_kg = db.Column(db.Numeric(10, 4), nullable=False)
    total_cost = db.Column(db.Numeric(12, 2), nullable=False)
    remarks = db.Column(db.Text)

    item = db.relationship("FeedItem", back_populates="consumptions")

    def as_dict(self):
        qty_kg = float(self.quantity_kg or 0.0)
        c_kg = float(self.cost_per_kg or 0.0)
        return {
            "consumption_id": self.consumption_id,
            "date": _date_or_none(self.date),
            "item_id": self.item_id,
            "item_name": self.item.name if self.item else None,
            "category": self.item.category if self.item else None,
            "quantity_kg": qty_kg,
            "quantity_mt": round(qty_kg / 1000.0, 3),
            "cost_per_kg": c_kg,
            "cost_per_mt": round(c_kg * 1000.0, 2),
            "total_cost": _money_or_none(self.total_cost),
            "remarks": self.remarks,
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


class DailyEggOperation(db.Model, AuditMixin):
    __tablename__ = "daily_egg_operations"

    record_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    opening_stock = db.Column(db.Integer, default=0)
    eggs_produced = db.Column(db.Integer, nullable=False)
    damaged_eggs = db.Column(db.Integer, default=0)
    eggs_available = db.Column(db.Integer, nullable=False)
    eggs_sold = db.Column(db.Integer, default=0, nullable=False)
    closing_stock = db.Column(db.Integer, nullable=False)
    egg_price_per_unit = db.Column(db.Numeric(10, 2), nullable=False)
    actual_revenue = db.Column(db.Numeric(12, 2), nullable=False)
    remarks = db.Column(db.Text)

    def as_dict(self):
        return {
            "record_id": self.record_id,
            "date": _date_or_none(self.date),
            "opening_stock": self.opening_stock or 0,
            "eggs_produced": self.eggs_produced,
            "damaged_eggs": self.damaged_eggs or 0,
            "eggs_available": self.eggs_available,
            "eggs_sold": self.eggs_sold,
            "closing_stock": self.closing_stock,
            "egg_price_per_unit": _money_or_none(self.egg_price_per_unit),
            "actual_revenue": _money_or_none(self.actual_revenue),
            "remarks": self.remarks,
            "created_at": _datetime_or_none(self.created_at),
            "updated_at": _datetime_or_none(self.updated_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_deleted": self.is_deleted,
        }


