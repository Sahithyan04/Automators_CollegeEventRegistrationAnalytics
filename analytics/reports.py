"""
SQL-based report generation functions.
Each function takes a sqlite3 Connection and returns a pandas DataFrame.
"""

import pandas as pd


def registrations_per_event(conn) -> pd.DataFrame:
    """Total registrations per event."""
    query = """
        SELECT e.event_name, COUNT(r.id) AS total_registrations
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.event_name
        ORDER BY total_registrations DESC
    """
    return pd.read_sql_query(query, conn)


def attendance_per_event(conn) -> pd.DataFrame:
    """Total attendance (Present) per event."""
    query = """
        SELECT e.event_name, COUNT(a.id) AS total_attendance
        FROM events e
        LEFT JOIN attendance a ON e.id = a.event_id AND LOWER(a.attendance_status) = 'present'
        GROUP BY e.event_name
        ORDER BY total_attendance DESC
    """
    return pd.read_sql_query(query, conn)


def attendance_percentage(conn) -> pd.DataFrame:
    """Attendance percentage per event (attended / registered × 100)."""
    query = """
        SELECT
            e.event_name,
            COUNT(DISTINCT r.student_id) AS registered,
            COUNT(DISTINCT CASE WHEN LOWER(a.attendance_status) = 'present' THEN a.student_id END) AS attended,
            ROUND(
                CASE
                    WHEN COUNT(DISTINCT r.student_id) = 0 THEN 0
                    ELSE COUNT(DISTINCT CASE WHEN LOWER(a.attendance_status) = 'present' THEN a.student_id END) * 100.0
                         / COUNT(DISTINCT r.student_id)
                END, 1
            ) AS attendance_pct
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        LEFT JOIN attendance a ON e.id = a.event_id AND r.student_id = a.student_id
        GROUP BY e.event_name
        ORDER BY attendance_pct DESC
    """
    return pd.read_sql_query(query, conn)


def department_participation(conn) -> pd.DataFrame:
    """Registration count by department."""
    query = """
        SELECT s.department, COUNT(r.id) AS total_registrations
        FROM students s
        JOIN registrations r ON s.id = r.student_id
        GROUP BY s.department
        ORDER BY total_registrations DESC
    """
    return pd.read_sql_query(query, conn)


def year_wise_participation(conn) -> pd.DataFrame:
    """Registration count by academic year."""
    query = """
        SELECT s.year AS academic_year, COUNT(r.id) AS total_registrations
        FROM students s
        JOIN registrations r ON s.id = r.student_id
        GROUP BY s.year
        ORDER BY s.year
    """
    return pd.read_sql_query(query, conn)


def top_attended_events(conn, n: int = 5) -> pd.DataFrame:
    """Top N events by attendance count."""
    query = f"""
        SELECT e.event_name, COUNT(a.id) AS attendance_count
        FROM events e
        JOIN attendance a ON e.id = a.event_id AND LOWER(a.attendance_status) = 'present'
        GROUP BY e.event_name
        ORDER BY attendance_count DESC
        LIMIT {n}
    """
    return pd.read_sql_query(query, conn)


def invalid_records_summary(conn) -> pd.DataFrame:
    """Count of invalid records by reason."""
    query = """
        SELECT source, reason, COUNT(*) AS count
        FROM invalid_records
        GROUP BY source, reason
        ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)


def overall_stats(conn) -> dict:
    """Return high-level statistics as a dict."""
    counts = {}
    for table in ["students", "events", "registrations", "attendance", "invalid_records"]:
        row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        counts[table] = row[0]

    # Attendance rate
    reg_count = counts["registrations"]
    att_row = conn.execute(
        "SELECT COUNT(DISTINCT student_id || '-' || event_id) FROM attendance WHERE LOWER(attendance_status) = 'present'"
    ).fetchone()
    att_count = att_row[0] if att_row else 0

    counts["overall_attendance_rate"] = round(att_count / reg_count * 100, 1) if reg_count > 0 else 0.0
    return counts
