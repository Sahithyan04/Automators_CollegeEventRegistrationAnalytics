"""
Sample data generator for demo purposes.
Generates realistic registration and attendance CSVs with intentional messy data.
"""

import random
import pandas as pd
from datetime import datetime, timedelta
import io


def generate_sample_registrations(n: int = 160) -> pd.DataFrame:
    """
    Generate a sample registration CSV DataFrame with realistic messy data.
    Includes duplicates, missing values, mixed case, extra whitespace, etc.
    """
    random.seed(42)

    first_names = [
        "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun",
        "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
        "Ananya", "Diya", "Myra", "Sara", "Aadhya",
        "Priya", "Kavya", "Riya", "Neha", "Pooja",
        "Rahul", "Amit", "Sneha", "Meera", "Rohan",
        "Vikram", "Tanvi", "Nisha", "Karthik", "Deepak",
    ]
    last_names = [
        "Sharma", "Patel", "Gupta", "Singh", "Kumar",
        "Reddy", "Iyer", "Nair", "Joshi", "Verma",
        "Rao", "Mishra", "Das", "Mehta", "Bhat",
    ]
    domains = ["college.edu", "university.ac.in", "student.edu.in"]
    events_clean = ["AI Workshop", "Web Development Bootcamp", "Hackathon 2025", "Cybersecurity Seminar", "Data Science Summit"]
    # Messy variations of the same events
    events_messy = [
        "AI Workshop", "ai workshop", "AI_WORKSHOP", " AI  Workshop ",
        "Web Development Bootcamp", "web development bootcamp", "Web_Development_Bootcamp",
        "Hackathon 2025", "hackathon 2025", "HACKATHON_2025", "hackathon-2025",
        "Cybersecurity Seminar", "cybersecurity seminar", "CYBERSECURITY_SEMINAR",
        "Data Science Summit", "data science summit", "Data_Science_Summit", "DATA SCIENCE SUMMIT",
    ]
    departments_messy = [
        "CSE", "cse", "Computer Science", "computer science",
        "IT", "it", "Information Technology",
        "ECE", "ece", "Electronics", "electronics and communication",
        "ME", "mech", "Mechanical", "mechanical engineering",
        "EEE", "electrical", "Electrical Engineering",
    ]

    rows = []
    used_ids = set()
    base_date = datetime(2025, 3, 1)

    for i in range(n):
        first = random.choice(first_names)
        last = random.choice(last_names)

        # Messy name formatting
        name_fmt = random.choice([
            f"{first} {last}",
            f"  {first}  {last}  ",           # extra spaces
            f"{first.lower()} {last.lower()}", # all lowercase
            f"{first.upper()} {last.upper()}", # all uppercase
        ])

        # Email with some intentional issues
        email_base = f"{first.lower()}.{last.lower()}"
        email_roll = random.choice(["", str(random.randint(1, 999))])
        domain = random.choice(domains)
        email_choice = random.random()
        if email_choice < 0.05:
            email = ""  # Missing email
        elif email_choice < 0.08:
            email = f"{email_base}@"  # Invalid email
        elif email_choice < 0.11:
            email = f"@{domain}"  # Invalid email
        elif email_choice < 0.14:
            email = f"{email_base}{email_roll} @{domain}"  # Space in email
        else:
            email = f"{email_base}{email_roll}@{domain}"

        dept = random.choice(departments_messy)
        # Occasionally make department empty
        if random.random() < 0.04:
            dept = ""

        year = random.choice([1, 2, 3, 4])
        # Occasionally put invalid year
        if random.random() < 0.03:
            year = random.choice([0, 6, -1])

        event = random.choice(events_messy)
        reg_date = base_date + timedelta(days=random.randint(0, 30), hours=random.randint(8, 20))

        # Generate unique-ish registration ID
        reg_id = f"REG{str(i + 1).zfill(4)}"
        if reg_id in used_ids and random.random() < 0.5:
            reg_id = f"REG{str(i).zfill(4)}"  # duplicate ID sometimes
        used_ids.add(reg_id)

        rows.append({
            "registration_id": reg_id,
            "student_name": name_fmt,
            "email": email,
            "department": dept,
            "year": year,
            "event_name": event,
            "registration_date": reg_date.strftime("%Y-%m-%d %H:%M:%S"),
        })

    # ── Add explicit duplicates (same student + same event) ──
    for _ in range(8):
        dup = rows[random.randint(0, len(rows) - 1)].copy()
        dup["registration_id"] = f"REG{str(len(rows) + 1).zfill(4)}"
        rows.append(dup)

    # ── Add a few rows with mostly missing data ──
    for _ in range(3):
        rows.append({
            "registration_id": f"REG{str(len(rows) + 1).zfill(4)}",
            "student_name": "",
            "email": "",
            "department": "",
            "year": None,
            "event_name": random.choice(events_clean),
            "registration_date": "",
        })

    df = pd.DataFrame(rows)
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


def generate_sample_attendance(reg_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate attendance CSV based on registrations.
    - ~70% of registered students are marked Present
    - ~10% duplicate check-ins
    - ~5% unregistered attendees (new emails)
    - Mix of Present/Absent status
    """
    random.seed(99)

    rows = []
    base_date = datetime(2025, 4, 1)

    # Get valid registered emails (non-empty, has @)
    valid_regs = reg_df[reg_df["email"].str.contains("@", na=False)].copy()

    for _, reg in valid_regs.iterrows():
        # ~70% attend
        if random.random() < 0.70:
            status = "Present"
        else:
            if random.random() < 0.5:
                status = "Absent"
            else:
                continue  # No attendance record at all

        checkin = base_date + timedelta(
            days=random.randint(0, 15),
            hours=random.randint(8, 18),
            minutes=random.randint(0, 59),
        )

        # Messy status formatting
        status_fmt = random.choice([
            status,
            status.lower(),
            status.upper(),
            f"  {status}  ",
        ])

        rows.append({
            "email": reg["email"],
            "event_name": reg["event_name"],
            "checkin_time": checkin.strftime("%Y-%m-%d %H:%M:%S"),
            "attendance_status": status_fmt,
        })

    # ── Add duplicate check-ins ──
    if rows:
        for _ in range(10):
            dup = rows[random.randint(0, len(rows) - 1)].copy()
            dup["checkin_time"] = (
                base_date + timedelta(days=random.randint(0, 15), hours=random.randint(8, 18))
            ).strftime("%Y-%m-%d %H:%M:%S")
            rows.append(dup)

    # ── Add unregistered attendees ──
    events_clean = ["Ai Workshop", "Web Development Bootcamp", "Hackathon 2025", "Cybersecurity Seminar", "Data Science Summit"]
    for i in range(8):
        rows.append({
            "email": f"unregistered{i + 1}@college.edu",
            "event_name": random.choice(events_clean),
            "checkin_time": (base_date + timedelta(days=random.randint(0, 15))).strftime("%Y-%m-%d %H:%M:%S"),
            "attendance_status": "Present",
        })

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=99).reset_index(drop=True)
    return df


def get_sample_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to CSV bytes for download."""
    return df.to_csv(index=False).encode("utf-8")
