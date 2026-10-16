import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, 'poultry.db')
DEFAULT_SQLITE_URI = f"sqlite:///{DEFAULT_SQLITE_PATH.replace(os.sep, '/')}"

class Config:
    DATABASE_BACKEND = os.getenv('DATABASE_BACKEND', 'sqlite').lower()
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DEFAULT_SQLITE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'poultry-farm-secret-key-change-me')

    # Google Cloud & BigQuery settings
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID') or os.getenv('GOOGLE_CLOUD_PROJECT')
    BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'poultry_farm')
    GCP_REGION = os.getenv('GCP_REGION', 'us-central1')
    PORT = int(os.getenv('PORT', 8080))
