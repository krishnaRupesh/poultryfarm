# Poultry Farm Management & Finance

Comprehensive poultry farm management application for tracking:
- **Feed Inventory & Purchases**: Add, update, delete feed ingredients, monitor stock levels (in Metric Tons and kg), and track purchases using Weighted Average Cost (WAC).
- **Daily Feeding & Egg Operations**: Log active bird counts, daily feed consumed (e.g. 1 MT Corn + other ingredients), egg production, damaged eggs, and actual eggs sold (not assuming 100% sold).
- **Daily Cost-per-Bird & Cost-per-Egg Profitability Analysis**: Real-time calculations of feed spent per bird, production cost per egg generated, realized profit on actual sales, and unsold egg inventory valuation.
- **Sales & Finance**: Products, customer accounts, orders, payments, incident tracking, and balance sheets.

---

## Project Structure

```text
backend/     Flask API application, SQLAlchemy models, and SQLite database (poultry.db)
frontend/    Static HTML, CSS, and JavaScript screens
  css/       Application styling and KPI components
  js/        API client and UI controllers
  pages/     UI screens:
    inventory/    Feed inventory, daily operations, and cost analysis dashboards
    balances/     Customer balance sheets
    customers/    Customer management
    incidents/    Incident logging and tracking
    orders/       Order processing
    payments/     Payment entries
    products/     Product catalog
    rates/        Egg rate history
docs/        Planning notes and requirements
sql/         DDL schemas, audit tables & triggers, seed mock data, and DB initializers
```

---

## 1. Local SQLite Database Setup

SQLite is a serverless, zero-configuration database engine stored in `backend/poultry.db`.

### Initialize Tables and Triggers

Run the initializer to create all tables (including feed inventory, purchases, flock, feeding, egg operations), audit history tables, and automated triggers:

```powershell
python sql/init_sqlite_db.py
```

### Seed Realistic Mock Data (DML)

To populate feed ingredients (Corn, Soybean Meal, Rice Bran, Premix, etc.), sample purchases, 10,000 birds flock records, daily 1 MT feed consumption entries, and egg production/sales logs:

```powershell
python sql/seed_mock_data.py
```

*(Alternatively, run the pure SQL script `sql/seed_mock_data.sql` in any SQLite/Postgres client).*

---

## 2. Running the Backend

```powershell
cd backend
python run.py
```

- Flask API server runs at: `http://127.0.0.1:5000`
- Swagger UI API Documentation: `http://127.0.0.1:5000/apidocs`

### New API Endpoints:
- **Feed Inventory**:
  - `GET /api/feed/items`: List all feed ingredients with stock levels (MT & kg) and avg costs
  - `POST /api/feed/items`: Add new feed ingredient
  - `PUT /api/feed/items/<id>`: Update feed ingredient
  - `DELETE /api/feed/items/<id>`: Soft-delete feed ingredient
  - `GET /api/feed/purchases`: List purchase logs
  - `POST /api/feed/purchases`: Record purchase (accepts MT or kg, updates stock & weighted cost)
- **Daily Operations**:
  - `GET /api/daily/flock`: Active bird counts
  - `POST /api/daily/flock`: Save daily active birds count
  - `GET /api/daily/consumption`: List daily feed consumption
  - `POST /api/daily/consumption`: Record daily feed consumed (deducts stock)
  - `GET /api/daily/egg-operations`: Daily egg production and sales
  - `POST /api/daily/egg-operations`: Record eggs produced, damaged, sold, and market price
- **Daily Cost & Profitability Analysis**:
  - `GET /api/analysis/daily?date=YYYY-MM-DD`: Executive KPIs (Cost/bird, Cost/egg, Egg price, Realized profit, Unsold stock value, Diet breakdown)
  - `GET /api/analysis/history?days=14`: Historical trends and multi-day comparison

---

## 3. Running Automated Tests

Run the test suite covering feed items CRUD, purchases, flock tracking, feed consumption, egg operations with partial sales, and financial KPI calculations:

```powershell
python -m unittest backend/tests/test_feed_and_cost_analysis.py
```

---

## 4. Frontend Screens

Open [frontend/index.html](file:///c:/Users/tadik/PycharmProjects/poultryfarm/frontend/index.html) or run the Flask backend to access the application in your browser:
- **Feed Inventory**: `pages/inventory/feed-inventory.html`
- **Daily Feeding & Egg Ops**: `pages/inventory/daily-feed-production.html`
- **Daily Cost & Profitability Analysis**: `pages/inventory/daily-cost-analysis.html`
- **Dashboard**: `index.html`
