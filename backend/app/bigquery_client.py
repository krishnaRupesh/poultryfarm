"""
Google BigQuery Client Service for Poultry Farm Management.
Provides query execution, table insertion, and dataset operations.
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
                if isinstance(v, int):
                    query_params.append(bigquery.ScalarQueryParameter(k, "INT64", v))
                elif isinstance(v, float) or isinstance(v, Decimal):
                    query_params.append(bigquery.ScalarQueryParameter(k, "NUMERIC", v))
                elif isinstance(v, bool):
                    query_params.append(bigquery.ScalarQueryParameter(k, "BOOL", v))
                elif isinstance(v, date):
                    query_params.append(bigquery.ScalarQueryParameter(k, "DATE", v))
                else:
                    query_params.append(bigquery.ScalarQueryParameter(k, "STRING", str(v)))
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)

        query_job = client.query(sql, job_config=job_config)
        results = query_job.result()
        return [row_to_dict(row) for row in results]

    @staticmethod
    def insert_row(table_name: str, row: Dict[str, Any]) -> None:
        """Stream insert a single row into a BigQuery table."""
        client = get_bigquery_client()
        dataset = get_dataset_name()
        table_ref = f"{client.project}.{dataset}.{table_name}"

        # Clean row for JSON streaming
        cleaned = {}
        for k, v in row.items():
            if isinstance(v, (datetime, date)):
                cleaned[k] = v.isoformat()
            elif isinstance(v, Decimal):
                cleaned[k] = float(v)
            else:
                cleaned[k] = v

        errors = client.insert_rows_json(table_ref, [cleaned])
        if errors:
            raise RuntimeError(f"BigQuery insert error in {table_name}: {errors}")

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
                if isinstance(v, int):
                    query_params.append(bigquery.ScalarQueryParameter(k, "INT64", v))
                elif isinstance(v, (float, Decimal)):
                    query_params.append(bigquery.ScalarQueryParameter(k, "NUMERIC", v))
                elif isinstance(v, bool):
                    query_params.append(bigquery.ScalarQueryParameter(k, "BOOL", v))
                elif isinstance(v, date):
                    query_params.append(bigquery.ScalarQueryParameter(k, "DATE", v))
                else:
                    query_params.append(bigquery.ScalarQueryParameter(k, "STRING", str(v)))
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)

        job = client.query(sql, job_config=job_config)
        job.result()
        return job.num_dml_affected_rows or 0
