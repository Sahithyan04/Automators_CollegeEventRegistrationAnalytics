"""
Data cleaning functions for registration and attendance DataFrames.
Handles whitespace, case normalization, and empty row removal.
"""

import pandas as pd


def strip_and_lower(series: pd.Series) -> pd.Series:
    """Strip whitespace and convert to lowercase for a string Series."""
    return series.astype(str).str.strip().str.lower().replace("nan", pd.NA)


def normalize_whitespace(series: pd.Series) -> pd.Series:
    """Collapse multiple spaces into one and strip leading/trailing."""
    return series.astype(str).str.strip().str.replace(r"\s+", " ", regex=True).replace("nan", pd.NA)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: lowercase, strip, replace spaces with underscores."""
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^\w]", "_", regex=True)
    )
    return df


def clean_registrations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the registration DataFrame:
    - Normalize column names
    - Drop fully empty rows
    - Strip whitespace from all string columns
    - Lowercase email
    - Normalize student_name (title-case)
    """
    df = df.copy()
    df = clean_column_names(df)

    # Drop rows where ALL values are missing
    df = df.dropna(how="all").reset_index(drop=True)

    # String columns to clean
    str_cols = ["student_name", "email", "department", "event_name", "registration_id"]
    for col in str_cols:
        if col in df.columns:
            df[col] = normalize_whitespace(df[col])

    # Specific formatting
    if "email" in df.columns:
        df["email"] = df["email"].str.lower()

    if "student_name" in df.columns:
        df["student_name"] = df["student_name"].str.title()

    # Coerce year to numeric
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    return df


def clean_attendance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the attendance DataFrame:
    - Normalize column names
    - Drop fully empty rows
    - Strip whitespace from all string columns
    - Lowercase email
    - Normalize attendance_status to title-case
    """
    df = df.copy()
    df = clean_column_names(df)

    # Drop rows where ALL values are missing
    df = df.dropna(how="all").reset_index(drop=True)

    # String columns to clean
    str_cols = ["email", "event_name", "attendance_status"]
    for col in str_cols:
        if col in df.columns:
            df[col] = normalize_whitespace(df[col])

    # Specific formatting
    if "email" in df.columns:
        df["email"] = df["email"].str.lower()

    if "attendance_status" in df.columns:
        df["attendance_status"] = df["attendance_status"].str.title()

    return df
