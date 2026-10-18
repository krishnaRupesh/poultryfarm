"""
Google BigQuery Client Service for Poultry Farm Management.
Provides direct BigQuery query execution, standard DML insertion (avoiding streaming buffer locks),
updates, soft deletes, and restores.
"""
import os
import time
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

_client = None


def get_bigquery_client():
    global _client
    if _client is None:
        from google.cloud import bigquery
        project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        _client = bigquery.Client(project=project_id) if project_id else bigquery.Client()
    return _client


def get_dataset_name() -> str:
    return os.getenv("BIGQUERY_DATASET", "poultry_farm")


def generate_id() -> int:
    """Generate a high-resolution timestamp-based integer ID for BigQuery."""
    return int(time.time() * 1000)


def row_to_dict(row) -> Dict[str, Any]:
    """Convert BigQuery Row object to a JSON-serializable dictionary."""
    d = {}
    for key, val in row.items():
        if isinstance(val, (datetime, date)):
            d[key] = val.isoformat()
        elif isinstance(val, Decimal):
            d[key] = float(val)
        else:
            d[key] = val
    return d


class BigQueryService:
    @staticmethod
    def query(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        client = get_bigquery_client()
        dataset = get_dataset_name()

        # Format dataset placeholder
        sql = sql.replace("{dataset}", dataset)

        job_config = None
        if params:
            from google.cloud import bigquery
            query_params = []
            for k, v in params.items():
                if v is None:
                    query_params.append(bigquery.ScalarQueryParameter(k, "STRING", None))
                elif isinstance(v, int):
                    query_params.append(bigquery.ScalarQueryParameter(k, "INT64", v))
                elif isinstance(v, (float, Decimal)):
                    query_params.append(bigquery.ScalarQueryParameter(k, "NUMERIC", v))
                elif isinstance(v, bool):
                    query_params.append(bigquery.ScalarQueryParameter(k, "BOOL", v))
                elif isinstance(v, date):
                    query_params.append(bigquery.ScalarQueryParameter(k, "DATE", v))
                elif isinstance(v, datetime):
                    query_params.append(bigquery.ScalarQueryParameter(k, "TIMESTAMP", v))
                else:
                    query_params.append(bigquery.ScalarQueryParameter(k, "STRING", str(v)))
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)

        query_job = client.query(sql, job_config=job_config)
        results = query_job.result()
        return [row_to_dict(row) for row in results]

    @staticmethod
    def execute_dml(sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        client = get_bigquery_client()
        dataset = get_dataset_name()
        sql = sql.replace("{dataset}", dataset)

        job_config = None
        if params:
            from google.cloud import bigquery
            query_params = []
            for k, v in params.items():
                if v is None:
                    query_params.append(bigquery.ScalarQueryParameter(k, "STRING", None))
                elif isinstance(v, int):
                    query_params.append(bigquery.ScalarQueryParameter(k, "INT64", v))
                elif isinstance(v, (float, Decimal)):
                    query_params.append(bigquery.ScalarQueryParameter(k, "NUMERIC", v))
                elif isinstance(v, bool):
                    query_params.append(bigquery.ScalarQueryParameter(k, "BOOL", v))
                elif isinstance(v, date):
                    query_params.append(bigquery.ScalarQueryParameter(k, "DATE", v))
                elif isinstance(v, datetime):
                    query_params.append(bigquery.ScalarQueryParameter(k, "TIMESTAMP", v))
                else:
                    query_params.append(bigquery.ScalarQueryParameter(k, "STRING", str(v)))
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)

        job = client.query(sql, job_config=job_config)
        job.result()
        return job.num_dml_affected_rows or 0

    @classmethod
    def insert_record(cls, table_name: str, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard DML INSERT into BigQuery.
        Using DML instead of streaming insert ensures rows can be updated or deleted immediately
        without triggering BigQuery streaming buffer lockouts.
        """
        cols = list(row.keys())
        placeholders = [f"@{col}" for col in cols]
        sql = f"INSERT INTO `{{dataset}}.{table_name}` ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        cls.execute_dml(sql, row)
        return row

    @classmethod
    def update_record(cls, table_name: str, id_col: str, id_val: Any, updates: Dict[str, Any]) -> int:
        """Standard DML UPDATE in BigQuery."""
        updates["updated_at"] = datetime.utcnow()
        set_clauses = [f"{col} = @{col}" for col in updates.keys()]
        sql = f"UPDATE `{{dataset}}.{table_name}` SET {', '.join(set_clauses)} WHERE {id_col} = @target_id"
        params = dict(updates)
        params["target_id"] = id_val
        return cls.execute_dml(sql, params)

    @classmethod
    def soft_delete_record(cls, table_name: str, id_col: str, id_val: Any, deleted_by: str = "system") -> int:
        """Mark record as soft-deleted in BigQuery with timestamp and user."""
        sql = f"""
            UPDATE `{{dataset}}.{table_name}`
            SET is_deleted = TRUE,
                deleted_at = CURRENT_TIMESTAMP(),
                deleted_by = @deleted_by,
                updated_at = CURRENT_TIMESTAMP()
            WHERE {id_col} = @target_id
        """
        return cls.execute_dml(sql, {"target_id": id_val, "deleted_by": deleted_by})

    @classmethod
    def restore_record(cls, table_name: str, id_col: str, id_val: Any) -> int:
        """Restore a soft-deleted record in BigQuery."""
        sql = f"""
            UPDATE `{{dataset}}.{table_name}`
            SET is_deleted = FALSE,
                deleted_at = NULL,
                deleted_by = NULL,
                updated_at = CURRENT_TIMESTAMP()
            WHERE {id_col} = @target_id
        """
        return cls.execute_dml(sql, {"target_id": id_val})

    @classmethod
    def get_record(cls, table_name: str, id_col: str, id_val: Any) -> Optional[Dict[str, Any]]:
        sql = f"SELECT * FROM `{{dataset}}.{table_name}` WHERE {id_col} = @target_id LIMIT 1"
        rows = cls.query(sql, {"target_id": id_val})
        return rows[0] if rows else None

    @classmethod
    def list_records(
        cls,
        table_name: str,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False,
        deleted_only: bool = False,
        order_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        where_clauses = []
        params = {}

        if deleted_only:
            where_clauses.append("is_deleted = TRUE")
        elif not include_deleted:
            where_clauses.append("is_deleted = FALSE")

        if filters:
            for k, v in filters.items():
                if v is not None:
                    where_clauses.append(f"{k} = @filter_{k}")
                    params[f"filter_{k}"] = v

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        order_sql = f"ORDER BY {order_by}" if order_by else ""
        sql = f"SELECT * FROM `{{dataset}}.{table_name}` {where_sql} {order_sql}"
        return cls.query(sql, params if params else None)
