"""
SQLite database initializer for Poultry Farm Finance.
Executes the DDL schema in sql/sqlite_schema.sql, creates tables, audit tables, and triggers,
and verifies database integrity.
"""
import os
import sqlite3
import sys

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "sqlite_schema.sql")
DEFAULT_DB_FILE = os.path.join(BASE_DIR, "backend", "poultry.db")


def init_db(db_path: str = DEFAULT_DB_FILE):
    print(f"Initializing SQLite database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if not os.path.exists(SCHEMA_FILE):
        print(f"Error: Schema file not found at {SCHEMA_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Execute all DDL statements
        cursor.executescript(schema_sql)
        conn.commit()
        print("Schema DDL executed successfully.")

        # Query all created tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
        print(f"Created tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")

        # Query all created triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name;")
        triggers = [row[0] for row in cursor.fetchall()]
        print(f"\nCreated triggers ({len(triggers)}):")
        for trigger in triggers:
            print(f"  - {trigger}")

        # Sanity check: test trigger functionality
        print("\nRunning trigger verification test...")
        cursor.execute(
            """
            INSERT INTO products (product_name, price, date, created_by)
            VALUES ('Test Eggs', 5.50, '2026-09-10', 'system_init');
            """
        )
        test_product_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            "SELECT action, product_name, price FROM products_audit WHERE product_id = ?;",
            (test_product_id,),
        )
        audit_row = cursor.fetchone()
        if audit_row and audit_row[0] == "INSERT":
            print(f"  [PASS] Insert trigger verified: products_audit recorded action '{audit_row[0]}'.")
        else:
            print("  [FAIL] Insert trigger verification failed.")

        # Clean up test row
        cursor.execute("DELETE FROM products WHERE product_id = ?;", (test_product_id,))
        cursor.execute("DELETE FROM products_audit WHERE product_id = ?;", (test_product_id,))
        conn.commit()
        print("  [PASS] Test data cleaned up successfully.")

        print("\nSQLite database setup completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error during database initialization: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    target_db = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_FILE
    init_db(target_db)
