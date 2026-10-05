"""
Seed mock data for Poultry Farm Feed Inventory, Flock, Feeding, and Egg Operations.
Executes the DML script in sql/seed_mock_data.sql.
"""
import os
import sqlite3
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DML_FILE = os.path.join(os.path.dirname(__file__), "seed_mock_data.sql")
DEFAULT_DB_FILE = os.path.join(BASE_DIR, "backend", "poultry.db")


def seed_db(db_path: str = DEFAULT_DB_FILE):
    print(f"Seeding mock data into database: {db_path}")

    if not os.path.exists(DML_FILE):
        print(f"Error: Seed file not found at {DML_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(DML_FILE, "r", encoding="utf-8") as f:
        dml_sql = f.read()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.executescript(dml_sql)
        conn.commit()
        print("Mock data seeded successfully!")

        # Print summary counts
        cursor.execute("SELECT COUNT(*) FROM feed_items WHERE is_deleted = 0;")
        feed_items_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM feed_purchases WHERE is_deleted = 0;")
        purchases_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM daily_flock_status WHERE is_deleted = 0;")
        flock_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM daily_feed_consumption WHERE is_deleted = 0;")
        consumption_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM daily_egg_operations WHERE is_deleted = 0;")
        egg_ops_count = cursor.fetchone()[0]

        print(f"\nSummary of Seeded Records:")
        print(f"  - Feed Inventory Items:      {feed_items_count}")
        print(f"  - Feed Purchases:            {purchases_count}")
        print(f"  - Daily Flock Status Days:   {flock_count}")
        print(f"  - Feed Consumption Entries:  {consumption_count}")
        print(f"  - Egg Operations Days:       {egg_ops_count}")

    except Exception as e:
        conn.rollback()
        print(f"Error during seeding: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    target_db = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_FILE
    seed_db(target_db)
