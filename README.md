College Event Registration & Attendance Analytics Platform

A full-featured Streamlit web application for managing, cleaning, and analyzing college event registration and attendance data. Upload your CSV files, run the automated data pipeline, and gain instant insights through interactive dashboards and exportable reports.

Features

CSV Upload & Sample Data Generation — Upload your own registration and attendance CSVs, or generate realistic demo datasets with intentional messy data for testing.
Automated Data Pipeline — A single click runs the full Clean → Validate → Transform → Match → Load pipeline.
Data Cleaning — Standardizes formats, trims whitespace, and normalizes inconsistent values.
Validation — Detects invalid emails, missing required fields, and duplicate records across both datasets.
Attendance Matching — Cross-references registration and attendance records to compute actual turnout.
SQLite Database — All processed data is persisted in a local SQLite database via SQLAlchemy.
Interactive Dashboard with 5 analytics tabs:

Event-wise registrations vs. attendance
Department participation breakdown
Year-wise participation trends
Registration vs. attendance matching analysis
Advanced heatmaps and data quality summaries


Export — Download cleaned CSVs, invalid records, and multi-sheet Excel analytics reports.
Docker Support — Production-ready Docker and Docker Compose configuration included.


App Pages
PageDescriptionUpload & ProcessUpload CSVs or generate sample data, then run the pipelineRaw DataPreview the original uploaded data before processingCleaned DataInspect the cleaned and transformed datasetsInvalid RecordsReview flagged records with their rejection reasonsDashboardExplore charts, trends, and analytics across 5 tabsExportDownload cleaned data and Excel reports

Tech Stack
LayerTechnologyFrontendStreamlitChartsPlotlyData ProcessingPandas, NumPyDatabaseSQLite via SQLAlchemyExcel Exportxlsxwriter, openpyxlContainerizationDocker, Docker ComposeRuntimePython 3.11

Getting Started
Option 1 — Docker (Recommended)
bash# Clone the repository
git clone https://github.com/your-username/college-event-analytics.git
cd college-event-analytics

# Build and start the container
docker compose up --build
Then open your browser at http://localhost:8501.
Data is persisted across restarts via Docker volumes (./database, ./uploads, ./exports).


Project Structure
college-event-analytics/
├── app.py                  # Main Streamlit application
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── database/
│   └── db.py               # SQLite init, connection, and table utilities
│
├── processing/
│   ├── clean.py            # Data cleaning logic
│   ├── validate.py         # Email, field, and duplicate validation
│   ├── transform.py        # Transformation pipeline
│   ├── match.py            # Registration ↔ attendance matching
│   └── load.py             # Database loaders
│
├── analytics/
│   ├── reports.py          # Aggregated report queries
│   └── attendance_analysis.py  # Match summaries, trends, heatmaps
│
├── charts/
│   └── charts.py           # Plotly chart builders
│
└── utils/
    └── sample_data.py      # Sample data generator

CSV Format
Registration CSV
ColumnDescriptionstudent_idUnique student identifiernameStudent full nameemailStudent email addressdepartmentDepartment / branchyearAcademic year (1–4)event_idEvent identifierevent_nameName of the event
Attendance CSV
ColumnDescriptionstudent_idUnique student identifieremailStudent email addressevent_idEvent identifierevent_nameName of the event


Analytics Overview

Registrations vs. Attendance — Side-by-side bar chart per event
Attendance Percentage — Percentage of registered students who actually attended
Top Attended Events — Ranked by absolute attendee count
Department Participation — Pie chart and leaderboard by department
Year-wise Participation — Breakdown by academic year
Matching Analysis — Matched, unmatched, and walk-in attendance counts
Event × Department Heatmap — Cross-tabulation of events and departments
Data Quality Summary — Count and chart of invalid records by reason
