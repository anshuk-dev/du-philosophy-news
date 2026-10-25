"""
Storage and Dashboard generator.
Manages persistent state in notices_history.json and updates README.md with detailed PDF breakdown.
"""

import json
import os
from typing import Dict, List, Tuple
from config import HISTORY_FILE, README_FILE, DU_PHILOSOPHY_COLLEGES
from models import VacancyNotice


def load_history() -> Dict[str, dict]:
    """Load previously discovered notices from notices_history.json."""
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Storage] Error reading history file: {e}")
        return {}


def save_history(history: Dict[str, dict]) -> None:
    """Save history back to notices_history.json."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Storage] Error writing history file: {e}")


def process_notices(scraped_notices: List[VacancyNotice]) -> Tuple[List[VacancyNotice], List[VacancyNotice]]:
    """Compares scraped notices with history and returns new & active notices."""
    history = load_history()
    new_notices: List[VacancyNotice] = []
    all_notices_dict: Dict[str, dict] = dict(history)

    for notice in scraped_notices:
        if notice.id not in history:
            new_notices.append(notice)
            all_notices_dict[notice.id] = notice.to_dict()
        else:
            # Update fields if new PDF or details were extracted
            existing = all_notices_dict[notice.id]
            for field in ["pdf_link", "vacancies_count", "category", "interview_date", "reporting_time", "venue", "deadline"]:
                val = getattr(notice, field, None)
                if val and val != "Check PDF" and val != "01 Post":
                    existing[field] = val
            all_notices_dict[notice.id] = existing

    save_history(all_notices_dict)

    all_active = [VacancyNotice.from_dict(d) for d in all_notices_dict.values()]
    all_active.sort(key=lambda n: n.discovered_at or "", reverse=True)

    return new_notices, all_active


def update_readme_dashboard(all_notices: List[VacancyNotice], last_checked: str) -> None:
    """Update README.md with detailed table of vacancies, category, interview date, and links."""
    table_rows = []
    for idx, n in enumerate(all_notices, 1):
        pdf_action = f"[📥 Download PDF]({n.pdf_link})" if n.pdf_link else "-"
        web_action = f"[🔗 Verification Page]({n.link})"
        title_esc = n.title.replace("|", "/")
        college_esc = n.college.replace("|", "/")
        cat_esc = n.category.replace("|", "/")
        venue_esc = n.venue.replace("|", "/")
        int_date_esc = n.interview_date.replace("|", "/")

        table_rows.append(
            f"| {idx} | **{college_esc}**<br>`{n.post_type}` | {title_esc} | **{n.vacancies_count}**<br>Category: `{cat_esc}` | "
            f"🗓️ **{int_date_esc}**<br>⏰ {n.reporting_time} | 📍 {venue_esc} | {pdf_action}<br>{web_action} |"
        )

    table_md = "\n".join(table_rows) if table_rows else "| - | - | *No active notices currently* | - | - | - | - |"

    colleges_list_md = "\n".join([f"- {col}" for col in DU_PHILOSOPHY_COLLEGES])

    readme_content = f"""# 🏛️ Delhi University (DU) Philosophy Faculty Vacancy Alert

> **100% Free Automated Tracker** with deep PDF extraction for Philosophy Guest Faculty, Ad-hoc Panels, and Permanent Assistant Professor vacancies across all Delhi University colleges.

[![DU Philosophy Vacancy Tracker](https://github.com/actions/workflows/du_philosophy_alert.yml/badge.svg)](https://github.com/actions/workflows/du_philosophy_alert.yml)
**Last Checked:** `{last_checked}`  
**Total Active Notices Tracked:** `{len(all_notices)}`  
**Direct Email Alerts to:** `anshu.philosophy@gmail.com`

---

## 📢 Current & Upcoming Philosophy Vacancies (Deep PDF Details)

| # | College & Post Type | Advertisement Title | Vacancies & Category | Interview Date & Time | Venue / Location | Official Links |
|---|---|---|---|---|---|---|
{table_md}

---

## 🎯 Coverage: DU Colleges with Philosophy Departments
{colleges_list_md}

---

## ⚡ How This Free Automation Works
1. **GitHub Actions Workflow** runs automatically 3 times a day (8:30 AM, 2:30 PM, 8:30 PM IST).
2. It scrapes:
   - Central DU Portal (`work-with-du`)
   - DU Colrec & Samarth Portal (`colrec.uod.ac.in` & `rec.uod.ac.in`)
   - DU Department of Philosophy (`philosophy.du.ac.in/notices`)
   - College portals & real-time RSS news feeds.
3. It strictly filters out expired/past notices and keeps only **Current & Upcoming** advertisements.
4. **Deep PDF & OCR Analysis**:
   - Number of vacancies (e.g. 01 Post, 02 Posts)
   - Reservation Category (UR, EWS, SC, ST, OBC)
   - Walk-in Interview Date & Time
   - Reporting Time & Venue (Principal's Office / Committee Room)
   - Verification Webpage URL & Direct Official PDF link
5. Sends an instant alert email to `anshu.philosophy@gmail.com` when a new notice is published.
"""

    try:
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(readme_content)
    except Exception as e:
        print(f"[Storage] Error writing README.md: {e}")
