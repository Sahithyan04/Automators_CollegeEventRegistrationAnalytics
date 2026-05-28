"""
Attendance-specific analysis functions.
"""

import pandas as pd


def get_match_summary(conn) -> pd.DataFrame:
    """
    Breakdown of registration vs attendance matching:
    - Registered & Attended
    - Registered but Absent
    - Attended without Registration
    """
    query = """
        SELECT
            'Registered & Attended' AS category,
            COUNT(*) AS count
        FROM registrations r
        JOIN attendance a ON r.student_id = a.student_id AND r.event_id = a.event_id
        WHERE LOWER(a.attendance_status) = 'present'

        UNION ALL

        SELECT
            'Registered but Absent' AS category,
            COUNT(*) AS count
        FROM registrations r
        LEFT JOIN attendance a ON r.student_id = a.student_id AND r.event_id = a.event_id
            AND LOWER(a.attendance_status) = 'present'
        WHERE a.id IS NULL

        UNION ALL

        SELECT
            'Attended without Registration' AS category,
            COUNT(*) AS count
        FROM attendance a
        LEFT JOIN registrations r ON a.student_id = r.student_id AND a.event_id = r.event_id
        WHERE r.id IS NULL AND LOWER(a.attendance_status) = 'present'
    """
    return pd.read_sql_query(query, conn)


def get_attendance_trends(conn) -> pd.DataFrame:
    """
    Attendance check-ins grouped by date (from checkin_time).
    """
    query = """
        SELECT
            DATE(checkin_time) AS checkin_date,
            COUNT(*) AS checkins
        FROM attendance
        WHERE LOWER(attendance_status) = 'present'
          AND checkin_time IS NOT NULL
          AND checkin_time != ''
        GROUP BY DATE(checkin_time)
        ORDER BY checkin_date
    """
    return pd.read_sql_query(query, conn)


def get_department_leaderboard(conn) -> pd.DataFrame:
    """
    Departments ranked by attendance rate (attended / registered × 100).
    """
    query = """
        SELECT
            s.department,
            COUNT(DISTINCT r.id) AS total_registered,
            COUNT(DISTINCT CASE WHEN LOWER(a.attendance_status) = 'present' THEN a.id END) AS total_attended,
            ROUND(
                CASE
                    WHEN COUNT(DISTINCT r.id) = 0 THEN 0
                    ELSE COUNT(DISTINCT CASE WHEN LOWER(a.attendance_status) = 'present' THEN a.id END) * 100.0
                         / COUNT(DISTINCT r.id)
                END, 1
            ) AS attendance_rate
        FROM students s
        JOIN registrations r ON s.id = r.student_id
        LEFT JOIN attendance a ON r.student_id = a.student_id AND r.event_id = a.event_id
        GROUP BY s.department
        ORDER BY attendance_rate DESC
    """
    return pd.read_sql_query(query, conn)


def get_event_department_heatmap(conn) -> pd.DataFrame:
    """
    Cross-tabulation of events × departments showing registration counts.
    Returns a pivot-style DataFrame.
    """
    query = """
        SELECT e.event_name, s.department, COUNT(r.id) AS reg_count
        FROM registrations r
        JOIN students s ON r.student_id = s.id
        JOIN events e ON r.event_id = e.id
        GROUP BY e.event_name, s.department
    """
    df = pd.read_sql_query(query, conn)
    if df.empty:
        return df
    return df.pivot_table(index="event_name", columns="department", values="reg_count", fill_value=0)
