# College Event Registration & Attendance Analytics Platform

A full-featured Streamlit web application for managing, cleaning, and analyzing college event registration and attendance data.

Upload your CSV files, run the automated data pipeline, and gain instant insights through interactive dashboards and exportable reports.

---

# Features

## CSV Upload & Sample Data Generation
- Upload your own registration and attendance CSVs
- Generate realistic demo datasets with intentionally messy data for testing

## Automated Data Pipeline
A single click runs the full:

```text
Clean → Validate → Transform → Match → Load
```

pipeline.

## Data Cleaning
- Standardizes formats
- Trims whitespace
- Normalizes inconsistent values

## Validation
Detects:
- Invalid emails
- Missing required fields
- Duplicate records across datasets

## Attendance Matching
Cross-references registration and attendance records to compute actual turnout.

## SQLite Database
All processed data is persisted in a local SQLite database using SQLAlchemy.

## Interactive Dashboard
Includes 5 analytics tabs:

- Event-wise registrations vs attendance
- Department participation breakdown
- Year-wise participation trends
- Registration vs attendance matching analysis
- Heatmaps and data quality summaries

## Export
Download:
- Cleaned CSVs
- Invalid records
- Multi-sheet Excel analytics reports

## Docker Support
Production-ready Docker and Docker Compose configuration included.

---

# App Pages

| Page | Description |
|------|-------------|
| Upload & Process | Upload CSVs or generate sample data, then run the pipeline |
| Raw Data | Preview original uploaded datasets |
| Cleaned Data | Inspect transformed and standardized data |
| Invalid Records | Review rejected records with reasons |
| Dashboard | Explore analytics and visualizations |
| Export | Download CSV and Excel reports |

---

# Tech Stack

| Layer | Technology |
|------|-------------|
| Frontend | Streamlit |
| Charts | Plotly |
| Data Processing | Pandas, NumPy |
| Database | SQLite + SQLAlchemy |
| Excel Export | xlsxwriter, openpyxl |
| Containerization | Docker, Docker Compose |
| Runtime | Python 3.11 |

---

# Getting Started

## Option 1 — Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/college-event-analytics.git

# Navigate into project
cd college-event-analytics

# Build and run containers
docker compose up --build
```

Open your browser at:

```text
http://localhost:8501
```

Data persists across restarts using Docker volumes:

```text
./database
./uploads
./exports
```

---

# Project Structure

```text
college-event-analytics/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── database/
│   └── db.py
│
├── processing/
│   ├── clean.py
│   ├── validate.py
│   ├── transform.py
│   ├── match.py
│   └── load.py
│
├── analytics/
│   ├── reports.py
│   └── attendance_analysis.py
│
├── charts/
│   └── charts.py
│
└── utils/
    └── sample_data.py
```

---

# CSV Format

## Registration CSV

| Column | Description |
|------|-------------|
| student_id | Unique student identifier |
| name | Student full name |
| email | Student email address |
| department | Department / branch |
| year | Academic year (1–4) |
| event_id | Event identifier |
| event_name | Name of the event |

---

## Attendance CSV

| Column | Description |
|------|-------------|
| student_id | Unique student identifier |
| email | Student email address |
| event_id | Event identifier |
| event_name | Name of the event |

---

# Analytics Overview

## Registrations vs Attendance
Side-by-side bar chart comparing:
- Total registrations
- Actual attendance per event

## Attendance Percentage
Displays:
- Attendance rate per event
- Turnout efficiency

## Top Attended Events
Ranks events by:
- Highest attendee count

## Department Participation
Visualizes:
- Department-wise contribution
- Participation leaderboard

## Year-wise Participation
Shows trends across:
- 1st Year
- 2nd Year
- 3rd Year
- 4th Year

## Matching Analysis
Tracks:
- Matched records
- Unmatched registrations
- Walk-in attendees

## Event × Department Heatmap
Cross-tabulation analysis between:
- Events
- Departments

## Data Quality Summary
Highlights:
- Invalid records
- Duplicate entries
- Missing fields
- Validation failures

---

# Data Processing Workflow

```text
1. Upload CSV Files
        ↓
2. Data Cleaning
        ↓
3. Validation Checks
        ↓
4. Data Transformation
        ↓
5. Attendance Matching
        ↓
6. Database Storage
        ↓
7. Dashboard Analytics
        ↓
8. Export Reports
```

---

