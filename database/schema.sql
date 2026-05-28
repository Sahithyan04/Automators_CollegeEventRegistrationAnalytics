
-- College Event Registration & Attendance Analytics Platform
-- Database Schema

-- students: unique student records
CREATE TABLE IF NOT EXISTS students (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name  TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    department    TEXT NOT NULL,
    year          INTEGER NOT NULL
);

-- events: unique event records
CREATE TABLE IF NOT EXISTS events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name    TEXT NOT NULL UNIQUE
);

-- registrations: many-to-many between students and events
CREATE TABLE IF NOT EXISTS registrations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id   TEXT NOT NULL,
    student_id        INTEGER NOT NULL,
    event_id          INTEGER NOT NULL,
    registration_date TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (event_id)   REFERENCES events(id),
    UNIQUE(student_id, event_id)
);

-- attendance: check-in records linked to students and events
CREATE TABLE IF NOT EXISTS attendance (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id        INTEGER NOT NULL,
    event_id          INTEGER NOT NULL,
    checkin_time      TEXT,
    attendance_status TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (event_id)   REFERENCES events(id)
);

-- invalid_records: log of all rejected/problematic rows
CREATE TABLE IF NOT EXISTS invalid_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT NOT NULL,
    row_data    TEXT NOT NULL,
    reason      TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);
