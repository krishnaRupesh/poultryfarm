import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, 'poultry.db')
DEFAULT_SQLITE_URI = f"sqlite:///{DEFAULT_SQLITE_PATH.replace(os.sep, '/')}"

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DEFAULT_SQLITE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

