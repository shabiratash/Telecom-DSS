"""
Application configuration for the Afghanistan Telecom Churn Prediction and Retention System.

The application runs exclusively on MySQL (telecom_churn_db). You may override the
connection via the DATABASE_URL environment variable or the individual MYSQL_*
variables. If MySQL is unavailable the app will raise a database error instead of
falling back to any other store.
"""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    # ----- Core Flask -----
    SECRET_KEY = os.getenv("SECRET_KEY", "afg-telecom-churn-secret-key-change-me")
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # ----- Admin credentials (session auth) -----
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    # ----- Customer credentials (session auth) -----
    CUSTOMER_USERNAME = os.getenv("CUSTOMER_USERNAME", "customer")
    CUSTOMER_PASSWORD = os.getenv("CUSTOMER_PASSWORD", "customer123")

    # ----- Database -----
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB = os.getenv("MYSQL_DB", "telecom_churn_db")

    # MySQL only. No SQLite / fallback store.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    # ----- Paths -----
    ML_MODEL_DIR = os.path.join(BASE_DIR, "models_ml")
    ML_MODEL_PATH = os.path.join(ML_MODEL_DIR, "churn_model.pkl")
    DATASET_DIR = os.path.join(BASE_DIR, "dataset")
    DATASET_PATH = os.path.join(DATASET_DIR, "telecom_dataset.csv")
    UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

    ITEMS_PER_PAGE = 12
