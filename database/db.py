"""
Database connection and initialization utilities for SQLite.
"""

import sqlite3
import os

# Path to the database file and schema
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "college_events.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")


def get_connection():
    """Return a sqlite3 connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables defined in schema.sql if they don't exist."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def reset_db():
    """Drop all tables and recreate them (for re-processing)."""
    conn = get_connection()
    tables = ["invalid_records", "attendance", "registrations", "events", "students"]
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table};")
    conn.commit()
    conn.close()
    init_db()


def get_table_counts(conn):
    """Return a dict of table_name -> row_count for all tables."""
    tables = ["students", "events", "registrations", "attendance", "invalid_records"]
    counts = {}
    for table in tables:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]
    return counts
