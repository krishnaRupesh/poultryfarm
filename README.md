# Poultry Farm Finance

Finance application prototype for managing poultry farm products, customers, orders, payments, incidents, and customer balances.

## Project Structure

```text
backend/   Flask API application and SQLite database (poultry.db)
frontend/  Static HTML, CSS, and JavaScript screens
docs/      Planning notes and requirements drafts
sql/       PostgreSQL DDL scripts, SQLite schema, and database initializer
```

---

## 1. Local SQLite Database Setup

SQLite is a serverless, zero-configuration, self-contained database engine. The database is stored as a single local file (`backend/poultry.db`), so you do not need to install or run a separate database server process.

### Initialize Tables and Triggers

To create the SQLite database file and automatically run all DDL statements (creating base tables, audit history tables, and automated audit triggers):

```powershell
# From the project root directory
python sql/init_sqlite_db.py
```

This executes [sql/sqlite_schema.sql](file:///c:/Users/tadik/PycharmProjects/poultryfarm/sql/sqlite_schema.sql) and creates:

* **Core Tables (6)**:
  * `products`
  * `customers`
  * `orders`
  * `payments`
  * `incidents`
  * `customer_balance_summary`
* **Audit Tables (6)**:
  * `products_audit`
  * `customers_audit`
  * `orders_audit`
  * `payments_audit`
  * `incidents_audit`
  * `customer_balance_summary_audit`
* **Automated Audit Triggers (18)**:
  * `AFTER INSERT`, `AFTER UPDATE`, and `AFTER DELETE` triggers for each of the 6 tables to log historical actions and timestamps automatically.

### Inspecting the SQLite Database

You can inspect the database at any time using:

1. **Python**:
   ```powershell
   python -c "import sqlite3; conn = sqlite3.connect('backend/poultry.db'); print([row[0] for row in conn.execute('SELECT name FROM sqlite_master WHERE type=\'table\'').fetchall()]); conn.close()"
   ```

2. **SQLite CLI** (if installed on your system):
   ```powershell
   sqlite3 backend/poultry.db
   .tables
   SELECT * FROM products;
   SELECT * FROM products_audit;
   .exit
   ```

3. **Database GUI tools**: You can open `backend/poultry.db` in VS Code (SQLite Viewer extension), DB Browser for SQLite, or DBeaver.

---

## 2. Flask Service & SQLite Connection

The Flask backend is configured in [backend/app/config.py](file:///c:/Users/tadik/PycharmProjects/poultryfarm/backend/app/config.py) to automatically connect to `backend/poultry.db` by default.

### Configuration (`backend/app/config.py`)

```python
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, 'poultry.db')
DEFAULT_SQLITE_URI = f"sqlite:///{DEFAULT_SQLITE_PATH.replace(os.sep, '/')}"

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DEFAULT_SQLITE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
```

* **Default Behavior**: If no `DATABASE_URL` is set, Flask connects to `backend/poultry.db`.
* **Custom / PostgreSQL Override**: You can switch to PostgreSQL or an alternate SQLite file at any time by setting the `DATABASE_URL` environment variable:
  ```powershell
  # For PostgreSQL
  $env:DATABASE_URL="postgresql://username:password@localhost:5432/poultry_db"

  # Or for a custom SQLite file
  $env:DATABASE_URL="sqlite:///path/to/custom.db"
  ```

---

## 3. Running the Backend Service

1. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start the Flask Server**:
   ```powershell
   cd backend
   python run.py
   ```

3. **Explore Swagger UI API Docs**:
   * Open your browser and navigate to: [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)
   * The products API endpoints are accessible at `/api/products`.

---

## 4. Frontend

Static UI files reside in the `frontend/` directory. Open [frontend/index.html](file:///c:/Users/tadik/PycharmProjects/poultryfarm/frontend/index.html) in your browser or serve with a local web server to access the dashboard and forms.
