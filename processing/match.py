"""
Attendance matching logic: compare attendance records against registrations.
"""

import pandas as pd


def match_attendance(reg_df: pd.DataFrame, att_df: pd.DataFrame) -> dict:
    """
    Match attendance records against registration records using (email, event_name).

    Returns a dict with:
        - registered_and_attended: students who registered AND attended
        - registered_but_absent: students who registered but did NOT attend
        - attended_without_registration: students who attended WITHOUT registering
        - duplicate_attendance: duplicate check-in records (same email + event)
    """

    # ── 1. Detect duplicate attendance ────────────────────────────────
    att_deduped = att_df.drop_duplicates(subset=["email", "event_name"], keep="first")
    duplicate_attendance = att_df[
        att_df.duplicated(subset=["email", "event_name"], keep="first")
    ].reset_index(drop=True)

    # Only consider "Present" records for matching
    att_present = att_deduped[
        att_deduped["attendance_status"].str.lower() == "present"
    ].copy()

    # ── 2. Create key sets ────────────────────────────────────────────
    reg_keys = set(
        zip(reg_df["email"].str.lower(), reg_df["event_name"].str.lower())
    )
    att_keys = set(
        zip(att_present["email"].str.lower(), att_present["event_name"].str.lower())
    )

    # ── 3. Registered AND attended ────────────────────────────────────
    matched_keys = reg_keys & att_keys
    registered_and_attended = reg_df[
        reg_df.apply(
            lambda r: (str(r["email"]).lower(), str(r["event_name"]).lower()) in matched_keys,
            axis=1,
        )
    ].reset_index(drop=True)

    # ── 4. Registered but absent ──────────────────────────────────────
    absent_keys = reg_keys - att_keys
    registered_but_absent = reg_df[
        reg_df.apply(
            lambda r: (str(r["email"]).lower(), str(r["event_name"]).lower()) in absent_keys,
            axis=1,
        )
    ].reset_index(drop=True)

    # ── 5. Attended without registration ──────────────────────────────
    unreg_keys = att_keys - reg_keys
    attended_without_registration = att_present[
        att_present.apply(
            lambda r: (str(r["email"]).lower(), str(r["event_name"]).lower()) in unreg_keys,
            axis=1,
        )
    ].reset_index(drop=True)

    return {
        "registered_and_attended": registered_and_attended,
        "registered_but_absent": registered_but_absent,
        "attended_without_registration": attended_without_registration,
        "duplicate_attendance": duplicate_attendance,
    }
