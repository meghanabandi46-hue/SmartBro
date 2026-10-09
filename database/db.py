import os
import socket
import sqlite3
from config import Config

ACTIVE_ENGINE = None

def is_mysql_reachable(host, port, timeout=0.8):
    """Fast probe to check if MySQL port is open and listening."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def get_mysql_connection():
    """Connect to MySQL or fail loudly; never silently switch databases."""
    if not is_mysql_reachable(Config.MYSQL_HOST, Config.MYSQL_PORT):
        raise RuntimeError(
            f"MySQL is not reachable at {Config.MYSQL_HOST}:{Config.MYSQL_PORT}. "
            "Check the service and DB_ENGINE configuration."
        )
    try:
        import mysql.connector
        return mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            connection_timeout=3,
            autocommit=False
        )
    except Exception as exc:
        raise RuntimeError("Unable to connect to the configured MySQL database.") from exc

def get_sqlite_connection():
    """Establish connection to SQLite development database."""
    os.makedirs(os.path.dirname(Config.SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_db():
    """Open only the explicitly configured database; fail closed on bad config."""
    global ACTIVE_ENGINE
    engine = Config.DB_ENGINE
    if engine == 'sqlite':
        ACTIVE_ENGINE = 'sqlite'
        return get_sqlite_connection()
    if engine == 'mysql':
        conn = get_mysql_connection()
        ACTIVE_ENGINE = 'mysql'
        return conn
    raise RuntimeError("DB_ENGINE must be explicitly set to 'sqlite' or 'mysql'.")

def get_active_engine():
    global ACTIVE_ENGINE
    if ACTIVE_ENGINE is None:
        conn = get_db()
        conn.close()
    return ACTIVE_ENGINE

def _adapt_query(query, engine):
    """Converts %s placeholders to ? if engine is sqlite."""
    if engine == 'sqlite':
        return query.replace('%s', '?')
    return query

def query_all(query, params=None):
    """Execute a SELECT query and return all rows as list of dicts."""
    engine = get_active_engine()
    adapted = _adapt_query(query, engine)
    conn = get_db()
    cursor = conn.cursor()

    try:
        if params:
            cursor.execute(adapted, params)
        else:
            cursor.execute(adapted)

        if engine == 'mysql':
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            rows = [dict(row) for row in cursor.fetchall()]
        return rows
    finally:
        cursor.close()
        conn.close()

def query_one(query, params=None):
    """Execute a SELECT query and return a single row as a dict or None."""
    rows = query_all(query, params)
    return rows[0] if rows else None

def execute(query, params=None):
    """Execute an INSERT/UPDATE/DELETE query and return lastrowid."""
    engine = get_active_engine()
    adapted = _adapt_query(query, engine)
    conn = get_db()
    cursor = conn.cursor()

    try:
        if params:
            cursor.execute(adapted, params)
        else:
            cursor.execute(adapted)

        if engine == 'sqlite':
            conn.commit()
            last_id = cursor.lastrowid
        else:
            last_id = cursor.lastrowid
        return last_id
    finally:
        cursor.close()
        conn.close()

def init_sqlite_schema(conn):
    """Initializes SQLite schema if MySQL is offline."""
    cur = conn.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'class_teacher', 'subject_teacher', 'support')),
        email TEXT NOT NULL UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        year_level INTEGER DEFAULT 2,
        section TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        roll_number TEXT NOT NULL UNIQUE,
        class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        phone TEXT DEFAULT NULL,
        streak_days INTEGER DEFAULT 7
    );

    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        employee_id TEXT NOT NULL UNIQUE,
        department TEXT DEFAULT 'Computer Science',
        phone TEXT DEFAULT NULL
    );

    CREATE TABLE IF NOT EXISTS class_teacher_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
        class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        academic_year TEXT DEFAULT '2025-2026',
        UNIQUE(teacher_id, class_id)
    );

    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        icon TEXT DEFAULT '▤',
        color TEXT DEFAULT '#f5f3ff',
        ink TEXT DEFAULT '#7c3aed'
    );

    CREATE TABLE IF NOT EXISTS teacher_subject_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
        class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        UNIQUE(teacher_id, class_id, subject_id)
    );

    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        max_marks INTEGER NOT NULL DEFAULT 100,
        sequence_order INTEGER NOT NULL DEFAULT 1,
        assessment_date DATE DEFAULT NULL
    );

    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        marks_obtained REAL NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(assessment_id, student_id)
    );

    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        attended_classes INTEGER NOT NULL DEFAULT 0,
        total_classes INTEGER NOT NULL DEFAULT 0,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(student_id, subject_id)
    );

    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        order_index INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS student_topic_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
        completion_pct INTEGER NOT NULL DEFAULT 0,
        UNIQUE(student_id, topic_id)
    );

    CREATE TABLE IF NOT EXISTS student_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        note_text TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS class_teacher_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        note_text TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(teacher_id, student_id)
    );

    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_number TEXT NOT NULL UNIQUE,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        category TEXT NOT NULL,
        subject_line TEXT NOT NULL,
        description TEXT NOT NULL,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'open',
        assigned_to_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS ticket_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        author_name TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
