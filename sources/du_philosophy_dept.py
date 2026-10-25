"""
Scraper for Delhi University Department of Philosophy.
URL: https://www.philosophy.du.ac.in/notices
Strictly extracts only active vacancy advertisements and walk-in interviews.
Excludes student empanelment lists (such as 'Final List of Adhoc Panel').
"""

from typing import List
from urllib.parse import urljoin
import requests
import urllib3
from bs4 import BeautifulSoup

from config import REQUEST_HEADERS, REQUEST_TIMEOUT
from date_utils import is_strictly_ongoing_or_upcoming, NON_VACANCY_PATTERNS
from models import VacancyNotice
from pdf_analyzer import analyze_pdf_details

urllib3.disable_warnings()

PHILOSOPHY_DEPT_NOTICES_URL = "https://www.philosophy.du.ac.in/notices"


def scrape_philosophy_dept() -> List[VacancyNotice]:
    """Scrape Department of Philosophy notices strictly for upcoming/ongoing vacancies."""
    notices: List[VacancyNotice] = []
    seen_ids = set()

    try:
        resp = requests.get(
            PHILOSOPHY_DEPT_NOTICES_URL,
            headers=REQUEST_HEADERS,
            verify=False,
            timeout=REQUEST_TIMEOUT
        )
        if resp.status_code != 200:
            return notices

        soup = BeautifulSoup(resp.content, "html.parser")

        for element in soup.find_all(["p", "li", "div"]):
            text = element.get_text(" ", strip=True)
            if not text or len(text) < 10:
                continue

            # Must NOT be a candidate empanelment data list
            if any(p in text.lower() for p in NON_VACANCY_PATTERNS):
                continue

            links = element.find_all("a")
            for a in links:
                href = a.get("href", "").strip()
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue

                is_doc_link = any(x in href.lower() for x in ["userfiles", "drive.google.com", ".pdf", ".docx", "forms.gle"])
                if not is_doc_link:
                    continue

                full_url = urljoin("https://www.philosophy.du.ac.in/", href)

                # Must be an actual vacancy or interview announcement
                is_vac_notice = any(k in (text + href).lower() for k in [
                    "guest faculty", "walk-in", "assistant professor", "recruitment", "vacancy"
                ])
                if not is_vac_notice:
                    continue

                link_text = a.get_text(strip=True)
                clean_title = text.replace(link_text, "").strip(" -:,") or text

                # Analyze PDF for interview date and verify active status
                pdf_meta = analyze_pdf_details(full_url, title=clean_title, college_hint="Department of Philosophy, DU")
                if not pdf_meta.get("is_active", False):
                    continue

                notice_id = VacancyNotice.generate_id(clean_title, full_url, full_url)
                if notice_id not in seen_ids:
                    seen_ids.add(notice_id)
                    notices.append(VacancyNotice(
                        id=notice_id,
                        title=clean_title,
                        college="Department of Philosophy, DU",
                        post_type="Guest / Faculty Recruitment",
                        link=full_url,
                        pdf_link=full_url,
                        date_posted=pdf_meta.get("interview_date", "Upcoming"),
                        source="DU Philosophy Department Portal",
                        vacancies_count=pdf_meta.get("vacancies_count", "01 Post"),
                        category=pdf_meta.get("category", "All Eligible"),
                        interview_date=pdf_meta.get("interview_date", "See Notice"),
                        reporting_time=pdf_meta.get("reporting_time", "30 Mins Before"),
                        venue=pdf_meta.get("venue", "Department of Philosophy, DU"),
                        deadline=pdf_meta.get("deadline", "Walk-in Interview")
                    ))

    except Exception as e:
        print(f"[Philosophy Dept] Error: {e}")

    return notices
