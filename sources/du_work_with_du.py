"""
Scraper for Delhi University Central Portal (Work with DU).
URL: https://www.du.ac.in/index.php?page=work-with-du
Extracts current and upcoming Philosophy faculty / guest notices and direct PDF links.
"""

from typing import List, Optional
from urllib.parse import urljoin
import requests
import urllib3
from bs4 import BeautifulSoup

from config import REQUEST_HEADERS, REQUEST_TIMEOUT, PHILOSOPHY_KEYWORDS, DU_PHILOSOPHY_COLLEGES
from date_utils import is_current_or_upcoming
from models import VacancyNotice

urllib3.disable_warnings()

WORK_WITH_DU_URL = "https://www.du.ac.in/index.php?page=work-with-du"
STATIC_FOOTER_PATTERNS = [
    "pmrf", "covid", "sc_st", "welfare", "sanctioned", "identity",
    "digital-sansad", "startups", "suraksha", "refund", "sgrc",
    "u5_section", "directions", "handbook", "regulation"
]


def extract_college_name(text: str) -> str:
    """Extract college or department name from notice title."""
    for college in DU_PHILOSOPHY_COLLEGES:
        simple_name = college.split("(")[0].strip()
        if simple_name.lower() in text.lower():
            return college

    if " - " in text:
        return text.split(" - ")[-1].strip()
    if ":-" in text:
        return text.split(":-")[-1].strip()
    if ":" in text:
        parts = text.split(":")
        if len(parts) > 1 and len(parts[-1].strip()) < 50:
            return parts[-1].strip()

    return "University of Delhi / Constituent College"


def extract_post_type(text: str) -> str:
    """Categorize the post type."""
    t = text.lower()
    if "guest" in t:
        return "Guest Faculty (Walk-in / Interview)"
    if "ad-hoc" in t or "adhoc" in t or "panel" in t:
        return "Ad-hoc / Panel Empanelment"
    if "walk-in" in t or "walk in" in t:
        return "Walk-in Interview"
    if "assistant professor" in t:
        return "Assistant Professor (Permanent / Regular)"
    if "professor" in t:
        return "Faculty Recruitment (Professor/Assoc. Prof)"
    return "Faculty Notice / Advertisement"


def get_pdf_from_article(article_url: str, article_title: str = "") -> Optional[str]:
    """Fetch article page to extract direct PDF link."""
    try:
        resp = requests.get(article_url, headers=REQUEST_HEADERS, verify=False, timeout=8)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.content, "html.parser")

        # 1. First priority: PDF link mentioning philosophy or matching article title
        for a in soup.find_all("a"):
            href = a.get("href", "").strip()
            text = a.get_text(strip=True).lower()
            if not href or ".pdf" not in href.lower():
                continue
            if any(p in href.lower() for p in STATIC_FOOTER_PATTERNS):
                continue

            if "philosophy" in href.lower() or "philosophy" in text or (article_title and article_title.lower()[:20] in text):
                return urljoin("https://www.du.ac.in/", href)

        # 2. Second priority: Any non-static PDF uploaded in 2026/2025/new-web
        for a in soup.find_all("a"):
            href = a.get("href", "").strip()
            if not href or ".pdf" not in href.lower():
                continue
            if any(p in href.lower() for p in STATIC_FOOTER_PATTERNS):
                continue
            if "uploads/" in href:
                return urljoin("https://www.du.ac.in/", href)

    except Exception:
        pass
    return None


def scrape_work_with_du() -> List[VacancyNotice]:
    """Scrape work-with-du page for current & upcoming Philosophy notices."""
    notices: List[VacancyNotice] = []
    seen_ids = set()

    try:
        resp = requests.get(WORK_WITH_DU_URL, headers=REQUEST_HEADERS, verify=False, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            print(f"[Work with DU] Failed with HTTP {resp.status_code}")
            return notices

        soup = BeautifulSoup(resp.content, "html.parser")

        # 1. Scrape Advertisement Tables (Table 0 and Table 1)
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for tr in rows[1:]:
                cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
                if len(cells) < 4:
                    continue

                advt_title = cells[0]
                pub_date = cells[1] if len(cells) > 1 else ""
                last_date = cells[2] if len(cells) > 2 else ""

                row_links = [urljoin("https://www.du.ac.in/", a.get("href", "").strip()) for a in tr.find_all("a") if a.get("href")]
                primary_link = row_links[0] if row_links else WORK_WITH_DU_URL
                pdf_link = next((l for l in row_links if ".pdf" in l.lower() and not any(p in l.lower() for p in STATIC_FOOTER_PATTERNS)), None)

                is_phil = any(k in advt_title.lower() for k in PHILOSOPHY_KEYWORDS)
                is_general_teaching = "assistant professor" in advt_title.lower() or "faculty" in advt_title.lower()

                if is_phil or (is_general_teaching and "non-teaching" not in advt_title.lower()):
                    is_current, date_str, status_tag = is_current_or_upcoming(
                        title=advt_title,
                        url=primary_link,
                        pdf_url=pdf_link,
                        deadline_str=last_date,
                        published_str=pub_date,
                        max_days_past=90
                    )

                    if is_current:
                        notice_id = VacancyNotice.generate_id(advt_title, primary_link, pdf_link)
                        if notice_id not in seen_ids:
                            seen_ids.add(notice_id)
                            notices.append(VacancyNotice(
                                id=notice_id,
                                title=advt_title,
                                college=extract_college_name(advt_title),
                                post_type=extract_post_type(advt_title),
                                link=primary_link,
                                pdf_link=pdf_link,
                                date_posted=date_str or pub_date or "Active",
                                source="DU Central Recruitment"
                            ))

        # 2. Scrape News / College Notice Links
        for a in soup.find_all("a"):
            text = a.get_text(" ", strip=True)
            href = a.get("href", "").strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            # Check if announcement concerns Philosophy
            if any(k in text.lower() for k in PHILOSOPHY_KEYWORDS) or any(k in href.lower() for k in PHILOSOPHY_KEYWORDS):
                full_link = urljoin("https://www.du.ac.in/", href)

                pdf_link = None
                if "mact=news" in full_link.lower() or "articleid" in full_link.lower():
                    pdf_link = get_pdf_from_article(full_link, text)
                elif ".pdf" in full_link.lower() and not any(p in full_link.lower() for p in STATIC_FOOTER_PATTERNS):
                    pdf_link = full_link

                is_current, date_str, status_tag = is_current_or_upcoming(
                    title=text,
                    url=full_link,
                    pdf_url=pdf_link,
                    max_days_past=120
                )

                if is_current:
                    notice_id = VacancyNotice.generate_id(text, full_link, pdf_link)
                    if notice_id not in seen_ids:
                        seen_ids.add(notice_id)
                        notices.append(VacancyNotice(
                            id=notice_id,
                            title=text,
                            college=extract_college_name(text),
                            post_type=extract_post_type(text),
                            link=full_link,
                            pdf_link=pdf_link,
                            date_posted=date_str or "Current Session",
                            source="DU Colleges Notice Board"
                        ))

    except Exception as e:
        print(f"[Work with DU] Error during scraping: {e}")

    return notices
