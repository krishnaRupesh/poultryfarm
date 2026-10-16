"""
BigQuery initializer and schema deployer for Poultry Farm Management.
Creates dataset, deploys DDL tables and analytical views from sql/bigquery_schema.sql,
and optionally seeds mock data.
"""
import os
import sys

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "bigquery_schema.sql")


def init_bigquery(project_id: str = None, dataset_id: str = "poultry_farm", seed_data: bool = True):
    try:
        from google.cloud import bigquery
    except ImportError:
        print("Error: google-cloud-bigquery is not installed. Run: pip install google-cloud-bigquery", file=sys.stderr)
        sys.exit(1)

    project_id = project_id or os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("Warning: GCP_PROJECT_ID not set. BigQuery client will use default project credentials.")

    print(f"Connecting to Google BigQuery (Project: {project_id or 'default'}, Dataset: {dataset_id})...")
    client = bigquery.Client(project=project_id) if project_id else bigquery.Client()
    project_id = client.project

    # 1. Ensure Dataset Exists
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset '{dataset_id}' exists.")
    except Exception:
        print(f"Creating dataset '{dataset_id}'...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = os.getenv("GCP_REGION", "US")
        dataset.description = "Poultry Farm Management & Finance Database"
        client.create_dataset(dataset, exists_ok=True)
        print(f"Dataset '{dataset_id}' created successfully.")

    # 2. Read and Execute Schema DDL
    if not os.path.exists(SCHEMA_FILE):
        print(f"Error: Schema file not found at {SCHEMA_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        ddl_content = f.read()

    # Replace placeholder dataset with target dataset
    ddl_content = ddl_content.replace("poultry_farm.", f"{dataset_id}.")

    # Split by statements
    statements = [stmt.strip() for stmt in ddl_content.split(";") if stmt.strip()]

    print(f"Executing {len(statements)} DDL statements...")
    for i, stmt in enumerate(statements, 1):
        try:
            query_job = client.query(stmt)
            query_job.result()
            first_line = stmt.split("\n")[0][:60]
            print(f"  [{i}/{len(statements)}] Executed: {first_line}...")
        except Exception as e:
            print(f"  [WARN] Statement {i} returned: {e}", file=sys.stderr)

    # 3. Seed Mock Data if requested
    if seed_data:
        print("\nSeeding initial data into BigQuery...")
        _seed_mock_bigquery(client, dataset_id)

    print("\nBigQuery setup completed successfully!")


def _seed_mock_bigquery(client, dataset_id: str):
    seed_sql = f"""
    -- Feed Items
    INSERT INTO `{dataset_id}.feed_items` (item_id, name, category, default_unit, current_stock_kg, average_cost_per_kg, reorder_level_kg, created_by, is_deleted)
    SELECT * FROM UNNEST([
        STRUCT(1 AS item_id, 'Yellow Corn' AS name, 'Grains' AS category, 'kg' AS default_unit, 8500.0 AS current_stock_kg, 0.28 AS average_cost_per_kg, 2000.0 AS reorder_level_kg, 'system' AS created_by, false AS is_deleted),
        STRUCT(2, 'Soybean Meal (48%)', 'Protein Meal', 'kg', 3200.0, 0.55, 1000.0, 'system', false),
        STRUCT(3, 'De-oiled Rice Bran (DORB)', 'Energy & Fiber', 'kg', 2400.0, 0.22, 800.0, 'system', false),
        STRUCT(4, 'Calcite Grit / Limestone', 'Minerals', 'kg', 1800.0, 0.09, 500.0, 'system', false),
        STRUCT(5, 'Layer Vitamin & Mineral Premix', 'Supplements', 'kg', 450.0, 1.80, 100.0, 'system', false)
    ])
    WHERE NOT EXISTS (SELECT 1 FROM `{dataset_id}.feed_items` WHERE is_deleted = false);

    -- Flock Status
    INSERT INTO `{dataset_id}.daily_flock_status` (status_id, date, active_birds, mortality, remarks, created_by, is_deleted)
    SELECT * FROM UNNEST([
        STRUCT(1 AS status_id, DATE '2026-10-05' AS date, 9986 AS active_birds, 3 AS mortality, 'Active flock count confirmed' AS remarks, 'system' AS created_by, false AS is_deleted)
    ])
    WHERE NOT EXISTS (SELECT 1 FROM `{dataset_id}.daily_flock_status` WHERE date = DATE '2026-10-05');

    -- Feed Consumption
    INSERT INTO `{dataset_id}.daily_feed_consumption` (consumption_id, date, item_id, quantity_kg, cost_per_kg, total_cost, remarks, created_by, is_deleted)
    SELECT * FROM UNNEST([
        STRUCT(1 AS consumption_id, DATE '2026-10-05' AS date, 1 AS item_id, 1000.0 AS quantity_kg, 0.28 AS cost_per_kg, 280.0 AS total_cost, '1 MT corn' AS remarks, 'system' AS created_by, false AS is_deleted),
        STRUCT(2, DATE '2026-10-05', 2, 250.0, 0.55, 137.5, 'Soybean meal', 'system', false),
        STRUCT(3, DATE '2026-10-05', 3, 160.0, 0.22, 35.2, 'Rice bran', 'system', false),
        STRUCT(4, DATE '2026-10-05', 4, 85.0, 0.09, 7.65, 'Calcite', 'system', false),
        STRUCT(5, DATE '2026-10-05', 5, 15.0, 1.80, 27.0, 'Premix', 'system', false)
    ])
    WHERE NOT EXISTS (SELECT 1 FROM `{dataset_id}.daily_feed_consumption` WHERE date = DATE '2026-10-05');

    -- Egg Operations
    INSERT INTO `{dataset_id}.daily_egg_operations` (record_id, date, opening_stock, eggs_produced, damaged_eggs, eggs_available, eggs_sold, closing_stock, egg_price_per_unit, actual_revenue, remarks, created_by, is_deleted)
    SELECT * FROM UNNEST([
        STRUCT(1 AS record_id, DATE '2026-10-05' AS date, 3185 AS opening_stock, 8840 AS eggs_produced, 35 AS damaged_eggs, 11990 AS eggs_available, 8000 AS eggs_sold, 3990 AS closing_stock, 0.078 AS egg_price_per_unit, 624.0 AS actual_revenue, 'Delivered to wholesale market' AS remarks, 'system' AS created_by, false AS is_deleted)
    ])
    WHERE NOT EXISTS (SELECT 1 FROM `{dataset_id}.daily_egg_operations` WHERE date = DATE '2026-10-05');
    """
    try:
        job = client.query(seed_sql)
        job.result()
        print("  Mock data verified/seeded successfully.")
    except Exception as e:
        print(f"  [Notice on seed]: {e}")


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else None
    dataset = sys.argv[2] if len(sys.argv) > 2 else os.getenv("BIGQUERY_DATASET", "poultry_farm")
    init_bigquery(project_id=proj, dataset_id=dataset)
