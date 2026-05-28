"""
Data transformation functions: event name normalization, department normalization, year validation.
"""

import re
import pandas as pd


# ── Department alias mapping ──────────────────────────────────────────────────
# Maps lowercase aliases → canonical department abbreviation
DEPARTMENT_ALIASES = {
    # Computer Science
    "cse": "CSE",
    "cs": "CSE",
    "computer science": "CSE",
    "computer science and engineering": "CSE",
    "comp sci": "CSE",
    "compsci": "CSE",
    # Information Technology
    "it": "IT",
    "information technology": "IT",
    "info tech": "IT",
    # Electronics & Communication
    "ece": "ECE",
    "electronics": "ECE",
    "electronics and communication": "ECE",
    "electronics & communication": "ECE",
    "ec": "ECE",
    # Electrical Engineering
    "eee": "EEE",
    "electrical": "EEE",
    "electrical engineering": "EEE",
    "electrical and electronics": "EEE",
    # Mechanical Engineering
    "me": "ME",
    "mech": "ME",
    "mechanical": "ME",
    "mechanical engineering": "ME",
    # Civil Engineering
    "ce": "CE",
    "civil": "CE",
    "civil engineering": "CE",
    # Artificial Intelligence & Data Science
    "aids": "AI&DS",
    "ai&ds": "AI&DS",
    "ai ds": "AI&DS",
    "ai and ds": "AI&DS",
    "artificial intelligence": "AI&DS",
    "artificial intelligence and data science": "AI&DS",
    # MBA
    "mba": "MBA",
    "management": "MBA",
    "business administration": "MBA",
}


def normalize_event_names(df: pd.DataFrame, col: str = "event_name") -> pd.DataFrame:
    """
    Normalize event names:
    - Lowercase → replace underscores/hyphens with spaces → collapse whitespace → title-case
    - e.g. "AI_WORKSHOP", "ai workshop", "ai-Workshop" all become "Ai Workshop"
    """
    df = df.copy()
    if col not in df.columns:
        return df

    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[_\-]+", " ", regex=True)   # underscores/hyphens → spaces
        .str.replace(r"\s+", " ", regex=True)       # collapse whitespace
        .str.strip()
        .str.title()
    )
    # Replace "nan" strings that came from NaN
    df[col] = df[col].replace("Nan", pd.NA)
    return df


def normalize_departments(df: pd.DataFrame, col: str = "department") -> pd.DataFrame:
    """
    Normalize department names using the alias mapping.
    Unrecognized departments are title-cased as-is.
    """
    df = df.copy()
    if col not in df.columns:
        return df

    def map_department(val):
        if pd.isna(val) or str(val).strip() == "":
            return pd.NA
        key = str(val).strip().lower()
        if key in DEPARTMENT_ALIASES:
            return DEPARTMENT_ALIASES[key]
        # If not in mapping, title-case it
        return str(val).strip().title()

    df[col] = df[col].apply(map_department)
    return df


def normalize_years(df: pd.DataFrame, col: str = "year") -> pd.DataFrame:
    """
    Coerce year to integer and validate range (1-5).
    Out-of-range values become NaN.
    """
    df = df.copy()
    if col not in df.columns:
        return df

    df[col] = pd.to_numeric(df[col], errors="coerce")
    # Set out-of-range years to NaN
    df.loc[~df[col].between(1, 5), col] = pd.NA
    return df


def apply_all_transformations(df: pd.DataFrame, is_registration: bool = True) -> pd.DataFrame:
    """
    Apply all transformations to a DataFrame.
    For registrations: normalize events, departments, and years.
    For attendance: normalize events only.
    """
    df = normalize_event_names(df, "event_name")
    if is_registration:
        df = normalize_departments(df, "department")
        df = normalize_years(df, "year")
    return df
