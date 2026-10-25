"""
Advanced PDF Text and OCR Analyzer for DU Philosophy Vacancy Notices.
Extracts:
  - Number of vacancies / posts
  - Reservation category (UR, EWS, OBC, SC, ST, PwBD)
  - Interview date & time
  - Reporting time
  - Venue / Location
  - Application deadline
  - Strict ongoing/upcoming validation (rejects past interviews and student lists)
"""

import os
import re
import subprocess
import tempfile
from datetime import datetime
from typing import Dict
import urllib3
import requests
import fitz

from date_utils import extract_date_from_string, is_strictly_ongoing_or_upcoming

urllib3.disable_warnings()

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def extract_raw_text_from_pdf(pdf_url: str) -> str:
    """Download PDF and extract text; fall back to OCR if scanned."""
    try:
        resp = requests.get(pdf_url, headers=REQUEST_HEADERS, verify=False, timeout=12)
        if resp.status_code != 200 or len(resp.content) < 100:
            return ""

        doc = fitz.open(stream=resp.content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"

        if len(text.strip()) > 80:
            return text

        if len(doc) > 0:
            pix = doc[0].get_pixmap(dpi=200)
            with tempfile.NamedTemporaryFile(suffix=".png") as tmp_img:
                pix.save(tmp_img.name)
                tesseract_bin = "/opt/homebrew/bin/tesseract" if os.path.exists("/opt/homebrew/bin/tesseract") else "tesseract"
                res = subprocess.run(
                    [tesseract_bin, tmp_img.name, "stdout", "-l", "eng"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout

    except Exception as e:
        print(f"[PDF Analyzer] Error extracting text from {pdf_url}: {e}")

    return ""


def analyze_pdf_details(pdf_url: str, title: str = "", college_hint: str = "") -> Dict[str, str]:
    """Analyzes vacancy notice PDF and strictly checks if it is ONGOING or UPCOMING."""
    defaults = {
        "is_active": False,
        "status_reason": "No PDF data",
        "vacancies_count": "01 Post",
        "category": "All Eligible / UR / Reserved",
        "interview_date": "Check Official Notice",
        "reporting_time": "30 Mins Before Interview",
        "venue": "Office of the Principal / Committee Room",
        "deadline": "",
        "verification_url": pdf_url
    }

    if not pdf_url:
        return defaults

    raw_text = extract_raw_text_from_pdf(pdf_url)
    if not raw_text:
        return defaults

    full_str = " ".join([l.strip() for l in raw_text.splitlines() if l.strip()])

    # 1. Number of Posts (Vacancies)
    post_count = "01 Post"
    m_p1 = re.search(r'Philosophy[^\d\n]{0,25}(\d{1,2})\b', full_str, re.IGNORECASE)
    if m_p1:
        post_count = f"{int(m_p1.group(1)):02d} Post(s)"
    else:
        m_p2 = re.search(r'\(0?([1-9])\s*-\s*Post', full_str, re.IGNORECASE)
        if m_p2:
            post_count = f"{int(m_p2.group(1)):02d} Post(s)"
        else:
            m_p3 = re.search(r'(\d{1,2})\s*(?:Posts?|Vacanc(?:y|ies))\b', full_str, re.IGNORECASE)
            if m_p3:
                post_count = f"{int(m_p3.group(1)):02d} Post(s)"

    # 2. Reservation Category
    category = "All Eligible Categories"
    cat_match = re.search(
        r'\b(EWS\s*(?:\([^\)]*\))?|SC\s*-\s*\d|1-UR|2-UR|UR\s*\(0?\d\)|UR|OBC|SC|ST|PwBD|All Categories)\b',
        full_str,
        re.IGNORECASE
    )
    if cat_match:
        c_found = cat_match.group(0).strip().upper()
        if "EWS" in c_found:
            category = "EWS (Economically Weaker Section)"
        elif "SC" in c_found:
            category = "SC (Scheduled Caste)"
        elif "ST" in c_found:
            category = "ST (Scheduled Tribe)"
        elif "OBC" in c_found:
            category = "OBC (Other Backward Class)"
        elif "UR" in c_found:
            category = "UR (Unreserved / General)"
        elif "ALL" in c_found:
            category = "All Categories (UR/SC/ST/OBC/EWS)"
        else:
            category = c_found

    # 3. Interview Date & Time
    interview_date = ""
    # Pattern A: e.g. Friday 10th July, 2026 at 10:30 a.m.
    dt_match_b = re.search(
        r'((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?\s*\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+20\d{2}(?:\s+at\s+\d{1,2}[:.]\d{2}\s*[APap]\.?[Mm]\.?)?)',
        full_str,
        re.IGNORECASE
    )
    # Pattern B: DD.MM.YYYY or DD/MM/YYYY at HH:MM AM/PM
    dt_match = re.search(
        r'(\d{1,2}[./-]\d{1,2}[./-](?:20)?\d{2}(?:\s*\([A-Za-z]+\))?(?:\s*(?:at)?\s*\d{1,2}[:.]\d{2}\s*(?:[APap]\.?[Mm]\.?))?)',
        full_str
    )
    if dt_match_b and ("at" in dt_match_b.group(0).lower() or len(dt_match_b.group(0)) > 12):
        interview_date = dt_match_b.group(0).strip()
    elif dt_match:
        interview_date = dt_match.group(0).strip()

    # 4. Reporting Time
    reporting_time = "30 Mins before interview"
    rep_match = re.search(r'Reporting Time:?\s*([0-9:APMapm\s.to-]+(?:[APap]\.?[Mm]\.?))', full_str, re.IGNORECASE)
    if rep_match:
        reporting_time = rep_match.group(1).strip()
    elif "report 30 minutes before" in full_str.lower():
        reporting_time = "Report 30 minutes before schedule"

    # 5. Application Deadline
    deadline = ""
    dl_match = re.search(r'latest by\s*([0-9A-Za-z,\s]+20\d{2})', full_str, re.IGNORECASE)
    if dl_match:
        deadline = dl_match.group(1).strip()

    # 6. Venue
    venue = f"Principal's Office / Committee Room, {college_hint or 'College Campus'}"
    if "in the office of the principal" in full_str.lower() or "office of the principal" in full_str.lower():
        venue = f"Office of the Principal, {college_hint or 'College'}"
    elif "committee room" in full_str.lower():
        venue = f"College Committee Room, {college_hint or 'College'}"
    elif "principal's office" in full_str.lower():
        venue = f"Principal's Office, {college_hint or 'College'}"

    # 7. STRICT VALIDATION: Is this notice ongoing or upcoming?
    is_active, status_reason = is_strictly_ongoing_or_upcoming(
        title=title or full_str[:100],
        interview_date_str=interview_date,
        deadline_str=deadline,
        full_text_hint=full_str[:400]
    )

    return {
        "is_active": is_active,
        "status_reason": status_reason,
        "vacancies_count": post_count,
        "category": category,
        "interview_date": interview_date or "Check Official Notice",
        "reporting_time": reporting_time,
        "venue": venue,
        "deadline": deadline or "Walk-in on Interview Date",
        "verification_url": pdf_url
    }
