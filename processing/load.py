"""
Load cleaned data into SQLite database.
"""

import json
import pandas as pd


def load_students(conn, df: pd.DataFrame):
    """
    Insert unique students into the students table.
    Uses INSERT OR IGNORE to skip duplicates by email.
    """
    students = df[["student_name", "email", "department", "year"]].drop_duplicates(subset=["email"])
    for _, row in students.iterrows():
        conn.execute(
            """INSERT OR IGNORE INTO students (student_name, email, department, year)
               VALUES (?, ?, ?, ?)""",
            (row["student_name"], row["email"], row["department"], int(row["year"]) if pd.notna(row["year"]) else 0),
        )
    conn.commit()


def load_events(conn, reg_df: pd.DataFrame, att_df: pd.DataFrame = None):
    """
    Insert unique events from both registration and attendance DataFrames.
    """
    events = set(reg_df["event_name"].dropna().unique())
    if att_df is not None:
        events |= set(att_df["event_name"].dropna().unique())

    for event_name in events:
        conn.execute(
            "INSERT OR IGNORE INTO events (event_name) VALUES (?)",
            (event_name,),
        )
    conn.commit()


def _get_student_id(conn, email: str):
    """Look up student ID by email."""
    row = conn.execute("SELECT id FROM students WHERE email = ?", (email,)).fetchone()
    return row[0] if row else None


def _get_event_id(conn, event_name: str):
    """Look up event ID by name."""
    row = conn.execute("SELECT id FROM events WHERE event_name = ?", (event_name,)).fetchone()
    return row[0] if row else None


def load_registrations(conn, df: pd.DataFrame):
    """
    Insert registration records with foreign key lookups.
    Skips rows where student or event can't be found.
    """
    for _, row in df.iterrows():
        student_id = _get_student_id(conn, row["email"])
        event_id = _get_event_id(conn, row["event_name"])
        if student_id and event_id:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO registrations
                       (registration_id, student_id, event_id, registration_date)
                       VALUES (?, ?, ?, ?)""",
                    (
                        row.get("registration_id", ""),
                        student_id,
                        event_id,
                        row.get("registration_date", ""),
                    ),
                )
            except Exception:
                pass  # Skip on unique constraint violation
    conn.commit()


def load_attendance(conn, df: pd.DataFrame):
    """
    Insert attendance records with foreign key lookups.
    """
    for _, row in df.iterrows():
        student_id = _get_student_id(conn, row["email"])
        event_id = _get_event_id(conn, row["event_name"])
        if student_id and event_id:
            conn.execute(
                """INSERT INTO attendance
                   (student_id, event_id, checkin_time, attendance_status)
                   VALUES (?, ?, ?, ?)""",
                (
                    student_id,
                    event_id,
                    row.get("checkin_time", ""),
                    row.get("attendance_status", ""),
                ),
            )
    conn.commit()


def load_invalid_records(conn, records: list):
    """
    Bulk insert invalid record entries.
    Each record should be a dict with keys: source, row_data (dict), reason.
    """
    for rec in records:
        conn.execute(
            """INSERT INTO invalid_records (source, row_data, reason)
               VALUES (?, ?, ?)""",
            (
                rec["source"],
                json.dumps(rec["row_data"]) if isinstance(rec["row_data"], dict) else str(rec["row_data"]),
                rec["reason"],
            ),
        )
    conn.commit()
