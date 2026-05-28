"""
Data validation functions: email regex, required fields, and duplicate detection.
"""

import re
import pandas as pd


# RFC-5322 simplified email regex
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_emails(df: pd.DataFrame, col: str = "email"):
    """
    Validate email addresses using regex.

    Returns:
        (valid_df, invalid_df) — rows with valid emails, rows with invalid emails.
    """
    df = df.copy()

    def is_valid_email(val):
        if pd.isna(val) or str(val).strip() == "":
            return False
        return bool(EMAIL_REGEX.match(str(val).strip()))

    mask = df[col].apply(is_valid_email)
    valid_df = df[mask].reset_index(drop=True)
    invalid_df = df[~mask].reset_index(drop=True)
    return valid_df, invalid_df


def validate_required_fields(df: pd.DataFrame, required_cols: list):
    """
    Check that required columns are not NaN or empty strings.

    Returns:
        (valid_df, invalid_df)
    """
    df = df.copy()

    # Build a mask: True if ALL required fields are present and non-empty
    mask = pd.Series([True] * len(df), index=df.index)
    for col in required_cols:
        if col in df.columns:
            col_mask = df[col].notna() & (df[col].astype(str).str.strip() != "")
            mask = mask & col_mask
        else:
            # Column doesn't exist → all rows are invalid
            mask = pd.Series([False] * len(df), index=df.index)
            break

    valid_df = df[mask].reset_index(drop=True)
    invalid_df = df[~mask].reset_index(drop=True)
    return valid_df, invalid_df


def detect_duplicates(df: pd.DataFrame, subset_cols: list):
    """
    Detect duplicate rows based on a subset of columns.

    Returns:
        (deduped_df, duplicate_df) — first occurrence kept, subsequent duplicates returned.
    """
    df = df.copy()
    dup_mask = df.duplicated(subset=subset_cols, keep="first")
    deduped_df = df[~dup_mask].reset_index(drop=True)
    duplicate_df = df[dup_mask].reset_index(drop=True)
    return deduped_df, duplicate_df
