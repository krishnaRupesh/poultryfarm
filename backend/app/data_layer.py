"""
Unified Data Access Layer for Poultry Farm Management.
Routes queries and writes to BigQuery (in Production / Cloud Run) or SQLite (in Local Development).
"""
import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Type

from flask import request
from .models import db
from .bigquery_client import BigQueryService, generate_id


def is_bigquery() -> bool:
    return os.getenv("DATABASE_BACKEND", "sqlite").lower() == "bigquery"


def list_records(
    table_name: str,
    model_class: Type[db.Model],
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    default_order=None,
) -> List[Dict[str, Any]]:
    """List records from BigQuery or SQLite based on configuration."""
    include_deleted = request.args.get("include_deleted", "").lower() == "true"
    deleted_only = request.args.get("deleted_only", "").lower() == "true"

    if is_bigquery():
        return BigQueryService.list_records(
            table_name=table_name,
            filters=filters,
            include_deleted=include_deleted,
            deleted_only=deleted_only,
            order_by=order_by,
        )

    # SQLite / SQLAlchemy Path
    query = model_class.query
    if hasattr(model_class, "is_deleted"):
        if deleted_only:
            query = query.filter_by(is_deleted=True)
        elif not include_deleted:
            query = query.filter_by(is_deleted=False)

    if filters:
        for k, v in filters.items():
            if v is not None and hasattr(model_class, k):
                query = query.filter(getattr(model_class, k) == v)

    if default_order is not None:
        query = query.order_by(default_order)

    records = query.all()
    return [r.as_dict() for r in records]


def get_record(
    table_name: str,
    model_class: Type[db.Model],
    id_col: str,
    id_val: Any,
) -> Optional[Dict[str, Any]]:
    """Fetch single record by ID."""
    if is_bigquery():
        return BigQueryService.get_record(table_name, id_col, id_val)

    rec = model_class.query.filter(getattr(model_class, id_col) == id_val).first()
    return rec.as_dict() if rec else None


def create_record(
    table_name: str,
    model_class: Type[db.Model],
    id_col: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Insert new record into BigQuery or SQLite."""
    now = datetime.utcnow()
    data.setdefault("created_at", now)
    data.setdefault("updated_at", now)
    data.setdefault("is_deleted", False)

    if is_bigquery():
        if id_col not in data or not data[id_col]:
            data[id_col] = generate_id()
        BigQueryService.insert_record(table_name, data)
        # Fetch fresh record
        fresh = BigQueryService.get_record(table_name, id_col, data[id_col])
        return fresh or data

    # SQLite Path
    rec = model_class(**data)
    db.session.add(rec)
    db.session.commit()
    return rec.as_dict()


def update_record(
    table_name: str,
    model_class: Type[db.Model],
    id_col: str,
    id_val: Any,
    updates: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Update record by ID."""
    now = datetime.utcnow()
    updates["updated_at"] = now

    if is_bigquery():
        BigQueryService.update_record(table_name, id_col, id_val, updates)
        return BigQueryService.get_record(table_name, id_col, id_val)

    rec = model_class.query.filter(getattr(model_class, id_col) == id_val).first()
    if not rec:
        return None
    for k, v in updates.items():
        if hasattr(rec, k):
            setattr(rec, k, v)
    db.session.commit()
    return rec.as_dict()


def soft_delete_record(
    table_name: str,
    model_class: Type[db.Model],
    id_col: str,
    id_val: Any,
    deleted_by: str = "system",
) -> bool:
    """Soft-delete record."""
    if is_bigquery():
        affected = BigQueryService.soft_delete_record(table_name, id_col, id_val, deleted_by)
        return affected > 0

    rec = model_class.query.filter(getattr(model_class, id_col) == id_val).first()
    if not rec:
        return False
    rec.is_deleted = True
    rec.deleted_at = datetime.utcnow()
    rec.deleted_by = deleted_by
    rec.updated_at = datetime.utcnow()
    db.session.commit()
    return True


def restore_record(
    table_name: str,
    model_class: Type[db.Model],
    id_col: str,
    id_val: Any,
) -> Optional[Dict[str, Any]]:
    """Restore soft-deleted record."""
    if is_bigquery():
        affected = BigQueryService.restore_record(table_name, id_col, id_val)
        return BigQueryService.get_record(table_name, id_col, id_val) if affected > 0 else None

    rec = model_class.query.filter(getattr(model_class, id_col) == id_val).first()
    if not rec:
        return None
    rec.is_deleted = False
    rec.deleted_at = None
    rec.deleted_by = None
    rec.updated_at = datetime.utcnow()
    db.session.commit()
    return rec.as_dict()
