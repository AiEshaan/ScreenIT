"""
resume_screening/extractor.py
-------------------------------
Feature extraction from parsed resume profiles.

Extracts numeric / categorical features needed for scoring:
  - experience_years  : total years computed from actual date ranges
  - education_level   : integer 0-4 with full degree-term normalization
  - jd_requirements   : required skills, years, and education from a JD

Design choices:
  - python-dateutil for robust date parsing (handles "Jan 2022", "2022", etc.)
  - Exhaustive education alias list covers all common resume degree formats
  - Experience calculation sums individual role durations (not calendar span)
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

try:
    from dateutil import parser as dateparser  # type: ignore
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False

from backend.app.ai.skills_database import extract_skills


# ── Education level taxonomy ──────────────────────────────────────────────────

# Ordered highest → lowest so first match wins
EDUCATION_LEVELS: dict[int, list[str]] = {
    4: [
        "phd", "ph.d", "ph.d.", "doctor", "doctorate", "d.phil",
        "doctor of philosophy", "doctor of science",
    ],
    3: [
        "master", "masters", "m.tech", "mtech", "m.e.", "m.e",
        "ms", "m.s.", "m.s", "msc", "m.sc.", "m.sc",
        "mba", "m.b.a", "m.b.a.", "master of", "postgraduate",
        "pg diploma", "m.eng", "m.eng.", "me",
    ],
    2: [
        "bachelor", "bachelors", "b.tech", "btech", "b.e.", "b.e",
        "be", "bs", "b.s.", "b.s", "bsc", "b.sc.", "b.sc",
        "b.com", "bcom", "b.ca", "bca", "bba", "b.b.a",
        "undergraduate", "b.eng", "b.eng.", "honours", "hons",
        "bachelor of", "b.a.", "ba",
    ],
    1: [
        "diploma", "associate", "associates", "associate's",
        "12th", "hsc", "higher secondary", "polytechnic",
        "junior college", "+2",
    ],
    0: [
        "10th", "ssc", "secondary", "high school", "matriculation",
    ],
}

EDUCATION_LABELS: dict[int, str] = {
    4: "Ph.D",
    3: "Master's",
    2: "Bachelor's",
    1: "Diploma / Associate",
    0: "High School",
}


def get_education_level(education_list: list[dict]) -> tuple[int, str]:
    """
    Determine the highest education level from parsed education entries.

    Args:
        education_list: list of dicts with keys 'degree', 'school', 'year'

    Returns:
        (level_int, human_readable_label)
        level_int: 0 (high school) → 4 (PhD), or -1 if not found
    """
    highest = -1
    label = "Not Specified"

    for edu in education_list:
        combined = (
            (edu.get("degree") or "") + " " + (edu.get("school") or "")
        ).lower()

        for level in sorted(EDUCATION_LEVELS.keys(), reverse=True):
            if any(term in combined for term in EDUCATION_LEVELS[level]):
                if level > highest:
                    highest = level
                    # Use the raw degree string if it's short and clean
                    raw = (edu.get("degree") or "").strip()
                    label = raw[:70] if raw and len(raw) < 70 else EDUCATION_LABELS[level]
                break

    return (max(highest, 0), label)


def get_experience_years(experience_list: list[dict]) -> float:
    """
    Compute total professional experience in years by summing role durations.

    Each role's duration is computed from its start/end date strings.
    Handles:  "Jan 2022 – Jun 2025",  "2020 – Present",  "2022"

    Returns:
        Total years (float, 1 decimal place)
    """
    if not experience_list:
        return 0.0

    total_months = 0

    for exp in experience_list:
        start_str = (exp.get("start") or "").strip()
        end_str = (exp.get("end") or "").strip()

        if not start_str:
            continue

        try:
            start_dt = _parse_date(start_str)
        except Exception:
            continue  # skip unparseable entries

        try:
            if end_str.lower() in ("present", "current", "now", ""):
                end_dt = datetime.now()
            else:
                end_dt = _parse_date(end_str)
        except Exception:
            end_dt = datetime.now()

        months = (
            (end_dt.year - start_dt.year) * 12
            + (end_dt.month - start_dt.month)
        )
        if months > 0:
            total_months += months

    return round(total_months / 12, 1)


def _parse_date(date_str: str) -> datetime:
    """Parse a date string to datetime, handles year-only and month-year formats."""
    date_str = date_str.strip()

    # Year only  →  assume January
    if re.match(r"^\d{4}$", date_str):
        return datetime(int(date_str), 1, 1)

    # Month Year abbreviation  →  e.g., "Jan 2022"
    month_year = re.match(
        r"^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?)\.?\s*(\d{4})$",
        date_str,
        re.IGNORECASE,
    )
    if month_year:
        return datetime.strptime(f"{month_year.group(1)[:3]} {month_year.group(2)}", "%b %Y")

    if DATEUTIL_AVAILABLE:
        return dateparser.parse(date_str, default=datetime(2000, 1, 1))

    # Fallback: just extract the year
    year_m = re.search(r"\d{4}", date_str)
    if year_m:
        return datetime(int(year_m.group(0)), 1, 1)

    raise ValueError(f"Cannot parse date: {date_str!r}")


# ── JD requirement extractor ──────────────────────────────────────────────────

def extract_jd_requirements(jd_text: str, role_title: str = "") -> dict:
    """
    Parse a job description into structured requirements.

    Returns:
        {
          role_title, required_skills, required_years,
          required_education_level, required_education_label, text
        }
    """
    required_skills = extract_skills(jd_text)
    required_years = _extract_required_years(jd_text)
    edu_level, edu_label = _extract_required_education(jd_text)

    # Try to extract role title from first line of JD if not provided
    if not role_title:
        first_line = jd_text.strip().split("\n")[0].strip()
        role_title = first_line[:80] if len(first_line) < 80 else "the position"

    return {
        "role_title": role_title,
        "required_skills": required_skills,
        "required_years": required_years,
        "required_education_level": edu_level,
        "required_education_label": edu_label,
        "text": jd_text,
    }


def _extract_required_years(jd_text: str) -> float:
    """Extract minimum experience requirement from JD prose."""
    patterns = [
        r"(\d+)\+?\s*years?\s+of\s+(?:relevant\s+)?(?:professional\s+)?experience",
        r"(\d+)\+?\s*years?\s+(?:professional\s+|industry\s+)?experience",
        r"minimum\s+(\d+)\s+years?",
        r"at\s+least\s+(\d+)\s+years?",
        r"(\d+)\s*[-–]\s*\d+\s+years?\s+of\s+experience",
        r"(\d+)\+\s*years?",
    ]
    for pattern in patterns:
        m = re.search(pattern, jd_text, re.IGNORECASE)
        if m:
            return float(m.group(1))
    return 1.0  # sensible default


def _extract_required_education(jd_text: str) -> tuple[int, str]:
    """Detect minimum education requirement in JD."""
    jd_lower = jd_text.lower()
    for level in sorted(EDUCATION_LEVELS.keys(), reverse=True):
        if any(term in jd_lower for term in EDUCATION_LEVELS[level]):
            return level, EDUCATION_LABELS[level]
    return 2, "Bachelor's"  # most roles default to Bachelor's
