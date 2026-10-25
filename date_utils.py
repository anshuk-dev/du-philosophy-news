"""
Date parsing and filtering utilities to ensure only CURRENT and UPCOMING
vacancies/notices are reported, filtering out expired/past notices.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Current reference year (2026)
CURRENT_YEAR = 2026
ACADEMIC_SESSIONS = ["2025-26", "2026-27", "2025-2026", "2026-2027", "2026"]


def extract_date_from_string(text: str) -> Optional[datetime]:
    """
    Extracts a date from text, URL, or filename.
    Supports:
      - DDMMYYYY (e.g. 07102026, 17082026)
      - DD.MM.YYYY or DD/MM/YYYY or DD-MM-YYYY
      - YYYY-MM-DD
    """
    if not text:
        return None

    # Pattern 1: DD.MM.YYYY or DD/MM/YYYY or DD-MM-YYYY
    m1 = re.search(r'\b(\d{1,2})[./-](\d{1,2})[./-](20\d{2})\b', text)
    if m1:
        d, m, y = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
        try:
            return datetime(y, m, d)
        except ValueError:
            pass

    # Pattern 2: DDMMYYYY in filenames (e.g. 07102026-ramjas, 17082026-lady)
    m2 = re.search(r'\b(\d{2})(\d{2})(20\d{2})\b', text)
    if m2:
        d, m, y = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        if 1 <= d <= 31 and 1 <= m <= 12 and 2020 <= y <= 2030:
            try:
                return datetime(y, m, d)
            except ValueError:
                pass

    # Pattern 3: YYYY-MM-DD
    m3 = re.search(r'\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b', text)
    if m3:
        y, m, d = int(m3.group(1)), int(m3.group(2)), int(m3.group(3))
        try:
            return datetime(y, m, d)
        except ValueError:
            pass

    return None


def is_current_or_upcoming(
    title: str,
    url: str,
    pdf_url: Optional[str] = None,
    deadline_str: Optional[str] = None,
    published_str: Optional[str] = None,
    max_days_past: int = 90
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Determines if a notice is CURRENT or UPCOMING, strictly excluding PAST/old notices.
    Returns:
      (is_valid, formatted_date_str, status_tag)
    """
    now = datetime.now()
    combined_text = f"{title} {url} {pdf_url or ''} {deadline_str or ''} {published_str or ''}".lower()

    # If explicitly mentioning an old academic year like 2020, 2021, 2022, 2023, 2024
    old_years = ["2020", "2021", "2022", "2023", "2024"]
    # Check if notice is exclusively from an old year without current session mentions
    has_current_session = any(sess in combined_text for sess in ["2025-26", "2026-27", "2025-2026", "2026-2027", "2026"])
    if not has_current_session:
        for oy in old_years:
            if f"-{oy}" in combined_text or f"_{oy}" in combined_text or f"/{oy}/" in combined_text or f" {oy} " in combined_text:
                return False, None, "Past/Expired"

    # Check deadline if available
    if deadline_str:
        deadline_dt = extract_date_from_string(deadline_str)
        if deadline_dt:
            if deadline_dt.date() >= now.date():
                return True, deadline_dt.strftime("%d-%m-%Y"), "Upcoming / Active Deadline"
            # If deadline passed recently (e.g. within 14 days), could be interview pending
            days_ago = (now.date() - deadline_dt.date()).days
            if days_ago <= 14:
                return True, deadline_dt.strftime("%d-%m-%Y"), "Recently Closed (Interviews in Progress)"
            else:
                return False, deadline_dt.strftime("%d-%m-%Y"), "Past/Expired"

    # Check publication date from published_str, URL or filename
    extracted_dt = None
    if published_str:
        extracted_dt = extract_date_from_string(published_str)
    if not extracted_dt and pdf_url:
        extracted_dt = extract_date_from_string(pdf_url)
    if not extracted_dt:
        extracted_dt = extract_date_from_string(url)
    if not extracted_dt:
        extracted_dt = extract_date_from_string(title)

    if extracted_dt:
        date_str = extracted_dt.strftime("%d-%m-%Y")
        diff_days = (now.date() - extracted_dt.date()).days

        # Future date or upcoming interview date
        if diff_days < 0:
            return True, date_str, "Upcoming Interview / Date"

        # Published recently (within last max_days_past days)
        if diff_days <= max_days_past:
            return True, date_str, "Current Active Notice"
        else:
            return False, date_str, "Past/Expired Notice"

    # If no specific date found, check for active session or fresh keywords
    if has_current_session:
        return True, "Current Session (2025-26 / 2026-27)", "Current Active Notice"

    # If completely undated and no current year signal, default to False to prevent past junk
    return False, None, "Unknown/Unverified Date"
