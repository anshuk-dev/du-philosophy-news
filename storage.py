"""
Storage and Dashboard generator.
Manages persistent state in notices_history.json and updates README.md.
"""

import json
import os
from datetime import datetime
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
    """
    Compares scraped notices with history.
    Returns:
      (new_notices, all_active_notices)
    """
    history = load_history()
    new_notices: List[VacancyNotice] = []
    all_notices_dict: Dict[str, dict] = dict(history)

    for notice in scraped_notices:
        if notice.id not in history:
            new_notices.append(notice)
            all_notices_dict[notice.id] = notice.to_dict()
        else:
            # Update fields if new PDF or info was resolved
            existing = all_notices_dict[notice.id]
            if not existing.get("pdf_link") and notice.pdf_link:
                existing["pdf_link"] = notice.pdf_link
            all_notices_dict[notice.id] = existing

    # Save updated history
    save_history(all_notices_dict)

    all_active = [VacancyNotice.from_dict(d) for d in all_notices_dict.values()]
    # Sort with most recent date first
    all_active.sort(key=lambda n: n.discovered_at or "", reverse=True)

    return new_notices, all_active


def update_readme_dashboard(all_notices: List[VacancyNotice], last_checked: str) -> None:
    """Update README.md with the latest DU Philosophy vacancy dashboard."""
    table_rows = []
    for idx, n in enumerate(all_notices, 1):
        pdf_action = f"[📥 Download PDF]({n.pdf_link})" if n.pdf_link else f"[🔗 View Notice]({n.link})"
        title_esc = n.title.replace("|", "/")
        college_esc = n.college.replace("|", "/")
        table_rows.append(
            f"| {idx} | **{college_esc}** | {title_esc} | `{n.post_type}` | {n.date_posted or 'Active'} | {pdf_action} |"
        )

    table_md = "\n".join(table_rows) if table_rows else "| - | - | *No active notices currently* | - | - | - |"

    colleges_list_md = "\n".join([f"- {col}" for col in DU_PHILOSOPHY_COLLEGES])

    readme_content = f"""# 🏛️ Delhi University (DU) Philosophy Faculty & Guest Vacancy Alert

> **100% Free Automated Tracker** for Philosophy Guest Faculty, Ad-hoc Panels, and Permanent Assistant Professor vacancies across all Delhi University colleges and departments.

[![DU Philosophy Vacancy Tracker](https://github.com/actions/workflows/du_philosophy_alert.yml/badge.svg)](https://github.com/actions/workflows/du_philosophy_alert.yml)
**Last Checked:** `{last_checked}`  
**Total Active Notices Tracked:** `{len(all_notices)}`  
**Direct Email Alerts to:** `anshu.philosophy@gmail.com`

---

## 📢 Current & Upcoming Philosophy Vacancies & Notices

| # | College / Department | Notice / Advertisement | Post Type | Date / Deadline | Official Link / PDF |
|---|---|---|---|---|---|
{table_md}

---

## 🎯 Coverage: DU Colleges with Philosophy Departments
This tracker monitors all recruitment boards, Central DU Portals, and Philosophy departments:
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
4. When a new notice is published, it **immediately sends an automatic email** to `anshu.philosophy@gmail.com` with:
   - College Name
   - Advertisement Title
   - Post Type (Guest Faculty / Assistant Professor / Ad-hoc Panel)
   - Direct Official PDF download link
5. It commits and updates this `README.md` dashboard with the latest active table.

---

## 📧 How to Setup Free Email Alerts
To enable automatic email delivery to your Gmail address completely free:
1. Go to your **Google Account** -> **Security** -> **2-Step Verification** -> **App Passwords**.
2. Create an App Password (Name: `DU Alert Bot`). Copy the 16-character password.
3. In your **GitHub Repository** -> Go to **Settings** -> **Secrets and variables** -> **Actions**.
4. Add two Repository Secrets:
   - `GMAIL_USER`: your gmail address (`anshu.philosophy@gmail.com`)
   - `GMAIL_APP_PASSWORD`: your 16-character Google App Password
5. That's all! Whenever a notice is released, you will get an email alert automatically.
"""

    try:
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(readme_content)
    except Exception as e:
        print(f"[Storage] Error writing README.md: {e}")
