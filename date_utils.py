"""
Date and Relevance validation utilities for DU Philosophy Faculty Vacancy Tracker.
Strictly ensures:
  1. Only ONGOING and UPCOMING vacancies are accepted (interview_date >= today or deadline >= today).
  2. Past/outdated vacancies whose interview/deadline has already passed are DISCARDED.
  3. Student/Candidate empanelment lists (e.g. 'Final List of Adhoc Panel') are DISCARDED.
"""

import re
from datetime import datetime
from typing import Optional, Tuple

# Candidate empanelment / non-vacancy patterns that must be ignored
NON_VACANCY_PATTERNS = [
    "final list of adhoc panel",
    "list of adhoc panel",
    "adhoc panel list",
    "list of candidates",
    "list of eligible candidates",
    "panel for making appointment as ad-hoc",
    "result notification",
    "screening result",
    "screening status",
    "phd interview results",
    "merit list",
    "datesheet",
    "time table",
    "syllabus",
    "gender champion",
    "orientation notice",
    "anti-ragging",
    "seminar flyer",
    "conference flyer",
]


def extract_date_from_string(text: str) -> Optional[datetime]:
    """Extracts date from string formatted as DD.MM.YYYY, DD-MM-YYYY, DD/MM/YYYY, or YYYY-MM-DD."""
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

    # Pattern 2: DDMMYYYY in filenames (e.g. 07102026, 17082026)
    m2 = re.search(r'\b(\d{2})(\d{2})(20\d{2})\b', text)
    if m2:
        d, m, y = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        if 1 <= d <= 31 and 1 <= m <= 12 and 2020 <= y <= 2030:
            try:
                return datetime(y, m, d)
            except ValueError:
                pass

    return None


def is_strictly_ongoing_or_upcoming(
    title: str,
    interview_date_str: Optional[str] = None,
    deadline_str: Optional[str] = None,
    published_str: Optional[str] = None,
    full_text_hint: str = ""
) -> Tuple[bool, str]:
    """
    Strictly determines if a vacancy notice is genuinely ONGOING or UPCOMING.
    Rejects:
      - Candidate lists / student empanelment data
      - Any notice whose interview date or deadline has already passed (< today)
    """
    today = datetime.now().date()
    combined_lower = f"{title} {full_text_hint}".lower()

    # 1. Filter out candidate/student empanelment lists
    for non_vac in NON_VACANCY_PATTERNS:
        if non_vac in combined_lower:
            return False, f"Candidate/Student data list, not a vacancy ({non_vac})"

    # 2. Check Interview Date
    if interview_date_str:
        interview_dt = extract_date_from_string(interview_date_str)
        if interview_dt:
            if interview_dt.date() < today:
                return False, f"Outdated/Expired: Interview was on {interview_dt.strftime('%d-%m-%Y')} (Passed)"
            else:
                return True, f"Upcoming Interview on {interview_dt.strftime('%d-%m-%Y')}"

    # 3. Check Application Deadline
    if deadline_str:
        deadline_dt = extract_date_from_string(deadline_str)
        if deadline_dt:
            if deadline_dt.date() < today:
                return False, f"Outdated/Expired: Deadline was {deadline_dt.strftime('%d-%m-%Y')} (Passed)"
            else:
                return True, f"Ongoing Application: Deadline {deadline_dt.strftime('%d-%m-%Y')}"

    # 4. Check if publication date is very recent (e.g. last 72 hours)
    if published_str:
        pub_dt = extract_date_from_string(published_str)
        if pub_dt:
            diff_days = (today - pub_dt.date()).days
            if diff_days < 0:
                return True, f"Upcoming Notice published for future ({pub_dt.strftime('%d-%m-%Y')})"
            if 0 <= diff_days <= 3:
                return True, f"Freshly Published Notice ({pub_dt.strftime('%d-%m-%Y')})"
            else:
                return False, f"Outdated: Published {diff_days} days ago without future interview date"

    return False, "No verified future interview date or deadline found"


def is_current_or_upcoming(
    title: str,
    url: str = "",
    pdf_url: Optional[str] = None,
    deadline_str: Optional[str] = None,
    published_str: Optional[str] = None,
    max_days_past: int = 3
) -> Tuple[bool, Optional[str], Optional[str]]:
    """Backward compatibility wrapper strictly enforcing ongoing/upcoming validation."""
    is_active, reason = is_strictly_ongoing_or_upcoming(
        title=title,
        interview_date_str=None,
        deadline_str=deadline_str,
        published_str=published_str,
        full_text_hint=f"{url} {pdf_url or ''}"
    )
    return is_active, deadline_str or published_str, reason
