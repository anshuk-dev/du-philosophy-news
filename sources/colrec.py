"""
Scraper for Delhi University Central Faculty Recruitment Portal (Colrec / Samarth).
URLs:
  - https://rec.uod.ac.in/
  - https://colrec.uod.ac.in/
Tracks centralized Assistant Professor permanent faculty recruitments across DU colleges.
"""

from typing import List
from urllib.parse import urljoin
import requests
import urllib3
from bs4 import BeautifulSoup

from config import REQUEST_HEADERS, REQUEST_TIMEOUT, DU_PHILOSOPHY_COLLEGES
from date_utils import is_current_or_upcoming
from models import VacancyNotice

urllib3.disable_warnings()

REC_PORTAL_PAGE = "https://rec.uod.ac.in/index.php/site/page?id=5df7427a9c7443d3bdc4fedb3c4a7bdc786c82532831873ba778af7a84cdab3b1"


def scrape_colrec() -> List[VacancyNotice]:
    """Scrape centralized college faculty recruitment advertisements."""
    notices: List[VacancyNotice] = []
    seen_ids = set()

    try:
        resp = requests.get(REC_PORTAL_PAGE, headers=REQUEST_HEADERS, verify=False, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return notices

        soup = BeautifulSoup(resp.content, "html.parser")

        # Find teaching posts section
        for a in soup.find_all("a"):
            text = a.get_text(" ", strip=True)
            href = a.get("href", "").strip()
            if not href or href == "#":
                continue

            full_link = urljoin("https://rec.uod.ac.in/", href)

            # Look for Assistant Professor entries
            if "assistant professor" in text.lower():
                # Get surrounding context or parent container
                parent = a.find_parent(["div", "li", "p"])
                context_text = parent.get_text(" · ", strip=True) if parent else text

                # Identify college
                college_name = "Delhi University Constituent College"
                for col in DU_PHILOSOPHY_COLLEGES:
                    simple = col.split("(")[0].strip().lower()
                    if simple in text.lower():
                        college_name = col
                        break

                # Check if current/upcoming
                is_current, date_str, status_tag = is_current_or_upcoming(
                    title=context_text,
                    url=full_link,
                    max_days_past=90
                )

                if is_current:
                    clean_title = f"{text} (Colrec / Teaching Vacancy)"
                    notice_id = VacancyNotice.generate_id(clean_title, full_link, "colrec")
                    if notice_id not in seen_ids:
                        seen_ids.add(notice_id)
                        notices.append(VacancyNotice(
                            id=notice_id,
                            title=clean_title,
                            college=college_name,
                            post_type="Assistant Professor (Permanent / Regular)",
                            link=full_link,
                            pdf_link="https://colrec.uod.ac.in/",
                            date_posted=date_str or "Active",
                            source="DU Central Colrec Portal"
                        ))

    except Exception as e:
        print(f"[Colrec Portal] Error: {e}")

    return notices
