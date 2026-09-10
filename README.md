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

## Backend

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
