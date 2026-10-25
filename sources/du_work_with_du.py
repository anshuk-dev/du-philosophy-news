"""
Scraper for Delhi University Central Portal (Work with DU).
URL: https://www.du.ac.in/index.php?page=work-with-du
Strictly extracts only ONGOING and UPCOMING Philosophy faculty notices.
Discards past expired interviews and candidate empanelment lists.
"""

from typing import List, Optional
from urllib.parse import urljoin
import requests
import urllib3
from bs4 import BeautifulSoup

from config import REQUEST_HEADERS, REQUEST_TIMEOUT, PHILOSOPHY_KEYWORDS, DU_PHILOSOPHY_COLLEGES
from date_utils import is_strictly_ongoing_or_upcoming, NON_VACANCY_PATTERNS
from models import VacancyNotice
from pdf_analyzer import analyze_pdf_details

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

        for a in soup.find_all("a"):
            href = a.get("href", "").strip()
            text = a.get_text(strip=True).lower()
            if not href or ".pdf" not in href.lower():
                continue
            if any(p in href.lower() for p in STATIC_FOOTER_PATTERNS):
                continue

            if "philosophy" in href.lower() or "philosophy" in text or (article_title and article_title.lower()[:20] in text):
                return urljoin("https://www.du.ac.in/", href)

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
    """Scrape work-with-du page strictly for ONGOING & UPCOMING notices."""
    notices: List[VacancyNotice] = []
    seen_ids = set()

    try:
        resp = requests.get(WORK_WITH_DU_URL, headers=REQUEST_HEADERS, verify=False, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
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

                # Ignore candidate data or non-vacancies
                if any(p in advt_title.lower() for p in NON_VACANCY_PATTERNS):
                    continue

                row_links = [urljoin("https://www.du.ac.in/", a.get("href", "").strip()) for a in tr.find_all("a") if a.get("href")]
                primary_link = row_links[0] if row_links else WORK_WITH_DU_URL
                pdf_link = next((l for l in row_links if ".pdf" in l.lower() and not any(p in l.lower() for p in STATIC_FOOTER_PATTERNS)), None)

                is_phil = any(k in advt_title.lower() for k in PHILOSOPHY_KEYWORDS)
                is_general_teaching = "assistant professor" in advt_title.lower() or "faculty" in advt_title.lower()

                if is_phil or (is_general_teaching and "non-teaching" not in advt_title.lower()):
                    is_active, status_reason = is_strictly_ongoing_or_upcoming(
                        title=advt_title,
                        deadline_str=last_date,
                        published_str=pub_date
                    )

                    if is_active:
                        college = extract_college_name(advt_title)
                        notice_id = VacancyNotice.generate_id(advt_title, primary_link, pdf_link)
                        if notice_id not in seen_ids:
                            seen_ids.add(notice_id)
                            notices.append(VacancyNotice(
                                id=notice_id,
                                title=advt_title,
                                college=college,
                                post_type=extract_post_type(advt_title),
                                link=primary_link,
                                pdf_link=pdf_link,
                                date_posted=last_date or pub_date or "Ongoing",
                                source="DU Central Recruitment",
                                vacancies_count="Multiple Teaching Posts",
                                category="UR / OBC / SC / ST / EWS",
                                interview_date="Apply Online Before Last Date",
                                reporting_time="Online Colrec Portal",
                                venue=f"{college} / Central Portal",
                                deadline=last_date
                            ))

        # 2. Scrape News / College Notice Links
        for a in soup.find_all("a"):
            text = a.get_text(" ", strip=True)
            href = a.get("href", "").strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            # Ignore candidate empanelment data
            if any(p in text.lower() for p in NON_VACANCY_PATTERNS):
                continue

            # Check if announcement concerns Philosophy
            if any(k in text.lower() for k in PHILOSOPHY_KEYWORDS) or any(k in href.lower() for k in PHILOSOPHY_KEYWORDS):
                full_link = urljoin("https://www.du.ac.in/", href)

                pdf_link = None
                if "mact=news" in full_link.lower() or "articleid" in full_link.lower():
                    pdf_link = get_pdf_from_article(full_link, text)
                elif ".pdf" in full_link.lower() and not any(p in full_link.lower() for p in STATIC_FOOTER_PATTERNS):
                    pdf_link = full_link

                college = extract_college_name(text)

                # Analyze PDF for exact interview date and ongoing validation
                pdf_meta = analyze_pdf_details(pdf_link, title=text, college_hint=college) if pdf_link else {}

                # STRICT CHECK: Only accept if ongoing or upcoming
                if not pdf_meta.get("is_active", False):
                    # Outdated / past interview -> Skip
                    continue

                notice_id = VacancyNotice.generate_id(text, full_link, pdf_link)
                if notice_id not in seen_ids:
                    seen_ids.add(notice_id)
                    notices.append(VacancyNotice(
                        id=notice_id,
                        title=text,
                        college=college,
                        post_type=extract_post_type(text),
                        link=full_link,
                        pdf_link=pdf_link,
                        date_posted=pdf_meta.get("interview_date", "Upcoming"),
                        source="DU Colleges Notice Board",
                        vacancies_count=pdf_meta.get("vacancies_count", "01 Post"),
                        category=pdf_meta.get("category", "All Eligible / Reserved"),
                        interview_date=pdf_meta.get("interview_date", "See Official Notice"),
                        reporting_time=pdf_meta.get("reporting_time", "30 Mins Before Interview"),
                        venue=pdf_meta.get("venue", f"Office of the Principal, {college}"),
                        deadline=pdf_meta.get("deadline", "Walk-in Interview")
                    ))

    except Exception as e:
        print(f"[Work with DU] Error during scraping: {e}")

    return notices
