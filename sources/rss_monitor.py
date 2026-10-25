"""
Google News RSS real-time monitor for DU Philosophy faculty announcements and walk-ins.
"""

from typing import List
import xml.etree.ElementTree as ET
import requests
import urllib3

from config import REQUEST_HEADERS, PHILOSOPHY_KEYWORDS, DU_PHILOSOPHY_COLLEGES
from date_utils import is_current_or_upcoming
from models import VacancyNotice

urllib3.disable_warnings()

RSS_QUERIES = [
    '("Philosophy" OR "दर्शनशास्त्र") ("Delhi University" OR "DU") ("Guest Faculty" OR "Assistant Professor" OR "walk-in")',
    '("Philosophy") ("Hindu College" OR "Miranda House" OR "Ramjas" OR "Hansraj" OR "Gargi" OR "LSR" OR "KMC") ("faculty" OR "interview")'
]


def scrape_rss_monitor() -> List[VacancyNotice]:
    """Fetch recent news announcements via free Google News RSS."""
    notices: List[VacancyNotice] = []
    seen_ids = set()

    for q in RSS_QUERIES:
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(q)}&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            resp = requests.get(url, headers=REQUEST_HEADERS, verify=False, timeout=10)
            if resp.status_code != 200:
                continue

            root = ET.fromstring(resp.content)
            items = root.findall(".//item")
            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""

                if not title or not link:
                    continue

                # Filter strictly for Philosophy faculty relevance
                t_lower = title.lower()
                is_phil = any(k in t_lower for k in PHILOSOPHY_KEYWORDS)
                is_fac = any(k in t_lower for k in ["faculty", "professor", "interview", "recruitment", "vacancy", "guest", "adhoc", "ad-hoc"])

                if not (is_phil and is_fac):
                    continue

                # Check if current/upcoming
                is_current, date_str, status_tag = is_current_or_upcoming(
                    title=title,
                    url=link,
                    published_str=pub_date,
                    max_days_past=45
                )

                if is_current:
                    # Detect college
                    college_name = "Delhi University"
                    for col in DU_PHILOSOPHY_COLLEGES:
                        simple = col.split("(")[0].strip().lower()
                        if simple in t_lower:
                            college_name = col
                            break

                    post_type = "Faculty News / Announcement"
                    if "guest" in t_lower:
                        post_type = "Guest Faculty (Walk-in)"
                    elif "assistant professor" in t_lower:
                        post_type = "Assistant Professor Vacancy"

                    notice_id = VacancyNotice.generate_id(title, link)
                    if notice_id not in seen_ids:
                        seen_ids.add(notice_id)
                        notices.append(VacancyNotice(
                            id=notice_id,
                            title=title,
                            college=college_name,
                            post_type=post_type,
                            link=link,
                            pdf_link=None,
                            date_posted=date_str or "Recent",
                            source="Web & News Monitor"
                        ))

        except Exception as e:
            print(f"[RSS Monitor] Error querying RSS: {e}")

    return notices
