"""
Main Orchestrator for Delhi University (DU) Philosophy Vacancy Tracker.
Coordinates scraping, active filtering, deduplication, email notification, and README update.
"""

import sys
from datetime import datetime
import pytz

from sources.du_work_with_du import scrape_work_with_du
from sources.du_philosophy_dept import scrape_philosophy_dept
from sources.colrec import scrape_colrec
from sources.rss_monitor import scrape_rss_monitor
from storage import process_notices, update_readme_dashboard
from notifier import send_email_alert


def get_current_ist_time() -> str:
    """Returns current timestamp in Indian Standard Time (IST)."""
    try:
        ist = pytz.timezone("Asia/Kolkata")
        return datetime.now(ist).strftime("%d %b %Y, %I:%M %p IST")
    except Exception:
        return datetime.now().strftime("%d %b %Y, %I:%M %p")


def main():
    start_time_str = get_current_ist_time()
    print("=" * 70)
    print(f"🏛️ DU Philosophy Faculty Vacancy Tracker Started at {start_time_str}")
    print("=" * 70)

    all_scraped = []

    # 1. Scrape Central DU Work with DU Portal
    print("\n[1/4] Checking DU Central Portal (work-with-du)...")
    try:
        work_notices = scrape_work_with_du()
        print(f"      Found {len(work_notices)} active notices.")
        all_scraped.extend(work_notices)
    except Exception as e:
        print(f"      Error: {e}")

    # 2. Scrape DU Philosophy Department Portal
    print("\n[2/4] Checking DU Philosophy Department (philosophy.du.ac.in)...")
    try:
        dept_notices = scrape_philosophy_dept()
        print(f"      Found {len(dept_notices)} active notices.")
        all_scraped.extend(dept_notices)
    except Exception as e:
        print(f"      Error: {e}")

    # 3. Scrape Central Colrec / Samarth Teaching Portal
    print("\n[3/4] Checking DU Colrec Portal (colrec.uod.ac.in)...")
    try:
        colrec_notices = scrape_colrec()
        print(f"      Found {len(colrec_notices)} active notices.")
        all_scraped.extend(colrec_notices)
    except Exception as e:
        print(f"      Error: {e}")

    # 4. Scrape Real-time Web / News Monitor
    print("\n[4/4] Checking Breaking News & Web Feeds (Google News RSS)...")
    try:
        rss_notices = scrape_rss_monitor()
        print(f"      Found {len(rss_notices)} notices.")
        all_scraped.extend(rss_notices)
    except Exception as e:
        print(f"      Error: {e}")

    print("\n" + "-" * 70)
    print(f"Total candidate notices collected: {len(all_scraped)}")

    # Deduplicate and check against history
    new_notices, all_active = process_notices(all_scraped)

    print(f"New notices detected this run: {len(new_notices)}")
    print(f"Total active notices currently tracked: {len(all_active)}")

    # Update README Dashboard
    update_readme_dashboard(all_active, start_time_str)
    print("✅ README.md dashboard updated.")

    # Send Notification if new notices found
    if new_notices:
        print(f"\n🚀 Sending email alert for {len(new_notices)} new notice(s)...")
        send_email_alert(new_notices)
    else:
        print("\nℹ️ No new notices since last check. Email alert not needed.")

    print("\n" + "=" * 70)
    print("🏁 Run completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
