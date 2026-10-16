# Production Multi-threaded Container for Google Cloud Run
FROM python:3.11-slim

# Prevent Python from buffering stdout and writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, frontend assets, and database schemas
COPY backend /app/backend
COPY frontend /app/frontend
COPY sql /app/sql

# Set working directory to backend where run.py and app package reside
WORKDIR /app/backend

# Initialize local SQLite if not already created (fallback for local container testing)
RUN python /app/sql/init_sqlite_db.py || true

# Expose port (Cloud Run sets $PORT dynamically)
EXPOSE 8080

# Run Gunicorn with recommended Cloud Run concurrency settings:
# 1 worker process with 8 threads, timeout disabled to allow Cloud Run to govern request timeout
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 8 --timeout 0 run:app
