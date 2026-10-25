"""
Scraper for Delhi University Department of Philosophy.
URL: https://www.philosophy.du.ac.in/notices
Extracts current session Ad-hoc Panel lists, empanelment notifications, and department interview schedules.
"""

from typing import List
from urllib.parse import urljoin
import requests
import urllib3
from bs4 import BeautifulSoup

from config import REQUEST_HEADERS, REQUEST_TIMEOUT
from date_utils import is_current_or_upcoming
from models import VacancyNotice

urllib3.disable_warnings()

PHILOSOPHY_DEPT_NOTICES_URL = "https://www.philosophy.du.ac.in/notices"


def scrape_philosophy_dept() -> List[VacancyNotice]:
    """Scrape Department of Philosophy notices page for current session panels and notices."""
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
            print(f"[Philosophy Dept] Failed with HTTP {resp.status_code}")
            return notices

        soup = BeautifulSoup(resp.content, "html.parser")

        # Notices are in list items or paragraphs containing links to userfiles, pdfs, or drive
        for element in soup.find_all(["p", "li", "div"]):
            text = element.get_text(" ", strip=True)
            if not text or len(text) < 10:
                continue

            # Look for links inside this block
            links = element.find_all("a")
            for a in links:
                href = a.get("href", "").strip()
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue

                # Must be a document or actionable notice link
                is_doc_link = any(x in href.lower() for x in ["userfiles", "drive.google.com", ".pdf", ".docx", "forms.gle"])
                if not is_doc_link:
                    continue

                full_url = urljoin("https://www.philosophy.du.ac.in/", href)

                # Check relevance: panel, ad-hoc, interview, guest, faculty, vacancy
                is_relevant = any(k in (text + href).lower() for k in [
                    "panel", "adhoc", "ad-hoc", "guest", "faculty", "interview",
                    "assistant", "recruitment", "appoint", "walk-in"
                ])
                if not is_relevant:
                    continue

                # Check if current or upcoming (skip old past sessions like 2023-24, 2021)
                is_current, date_str, status_tag = is_current_or_upcoming(
                    title=text,
                    url=full_url,
                    pdf_url=full_url if ".pdf" in full_url else None,
                    max_days_past=120
                )

                if is_current:
                    # Clean title
                    link_text = a.get_text(strip=True)
                    clean_title = text.replace(link_text, "").strip(" -:,")
                    if not clean_title or len(clean_title) < 5:
                        clean_title = text

                    post_type = "Ad-hoc Panel Empanelment"
                    if "guest" in clean_title.lower():
                        post_type = "Guest Faculty Notice"
                    elif "interview" in clean_title.lower():
                        post_type = "Interview Schedule / Result"
                    elif "assistant professor" in clean_title.lower():
                        post_type = "Assistant Professor Notice"

                    notice_id = VacancyNotice.generate_id(clean_title, full_url, full_url)
                    if notice_id not in seen_ids:
                        seen_ids.add(notice_id)
                        notices.append(VacancyNotice(
                            id=notice_id,
                            title=clean_title,
                            college="Department of Philosophy, DU",
                            post_type=post_type,
                            link=full_url,
                            pdf_link=full_url,
                            date_posted=date_str or "Current Session",
                            source="DU Philosophy Department Portal"
                        ))

    except Exception as e:
        print(f"[Philosophy Dept] Error during scraping: {e}")

    return notices
