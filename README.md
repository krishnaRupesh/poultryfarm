# Poultry Farm Finance

Finance application prototype for managing poultry farm products, customers, orders, payments, incidents, and customer balances.

## Project Structure

```text
backend/   Flask API application
frontend/  Static HTML, CSS, and JavaScript screens
docs/      Planning notes and requirements drafts
sql/       Initial PostgreSQL DDL scripts
```

## Backend

```powershell
cd backend
python run.py
```

By default, the Flask app runs at:

```text
http://localhost:5000
```

Useful local URLs:

```text
Frontend dashboard: frontend/index.html
Swagger API docs:   http://localhost:5000/apidocs
Products API:       http://localhost:5000/api/products/
```

The current API implementation is started with the products blueprint at `/api/products`.

## Database

PostgreSQL is expected to run locally on:

```text
localhost:5432
```

Default local database URL:

```text
postgresql://username:password@localhost:5432/poultry_db
```

Set `DATABASE_URL` in your environment or `.env` file if your local database name, user, or password is different.
