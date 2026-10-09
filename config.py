import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration with MySQL primary and SQLite development fallback."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'udaan-secret-key-2026-secure-session-salt')
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # MySQL Database Settings (Primary)
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'udaan_db')
    
    # Database Engine selection ('mysql' or 'sqlite')
    # If MYSQL is unreachable or DB_ENGINE is explicitly 'sqlite', falls back gracefully.
    DB_ENGINE = os.getenv('DB_ENGINE', 'auto')
    SQLITE_PATH = os.path.join(BASE_DIR, 'database', 'udaan.db')
