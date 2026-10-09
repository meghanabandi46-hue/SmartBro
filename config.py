import os
import secrets
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _truthy(name, default="0"):
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Environment-driven Flask and database configuration."""
    ENV = os.getenv("FLASK_ENV", "development").strip().lower()
    IS_PRODUCTION = ENV == "production"

    # Never use a predictable fallback secret. Local development gets an ephemeral key;
    # production must provide a stable secret via the environment.
    _secret = os.getenv("SECRET_KEY", "").strip()
    if IS_PRODUCTION and not _secret:
        raise RuntimeError("SECRET_KEY must be set in production.")
    SECRET_KEY = _secret or secrets.token_hex(32)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_PRODUCTION or _truthy("SESSION_COOKIE_SECURE")
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8

    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "udaan_db")

    # Use sqlite for local development by default. Set DB_ENGINE=mysql explicitly in
    # production; it must fail loudly rather than silently switching databases.
    DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").strip().lower()
    SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(BASE_DIR, "database", "udaan.db"))
    LOGIN_MAX_ATTEMPTS = int(os.getenv("LOGIN_MAX_ATTEMPTS", "8"))
    LOGIN_WINDOW_SECONDS = int(os.getenv("LOGIN_WINDOW_SECONDS", "300"))
