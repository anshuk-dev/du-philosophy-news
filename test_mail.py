"""
Quick Test Mailer Script.
Sends a sample DU Philosophy Vacancy Alert email to anshu.philosophy@gmail.com.
"""

import sys
import os
from config import GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL
from models import VacancyNotice
from notifier import send_email_alert

def main():
    print("=" * 60)
    print("🧪 Testing Direct Email Alert to:", RECIPIENT_EMAIL)
    print("=" * 60)

    # Sample active notices for the test
    sample_notices = [
        VacancyNotice(
            id="test-ramjas-01",
            title="Advertisement for the Post of Guest faculty in the Department of Philosophy - Ramjas College",
            college="Ramjas College",
            post_type="Guest Faculty (Walk-in / Interview)",
            link="https://www.du.ac.in/index.php?mact=News,cntnt01,detail,0&cntnt01articleid=18956&cntnt01returnid=219",
            pdf_link="https://www.du.ac.in/uploads/new-web/07102026-ramjas-guest-philosophy.pdf",
            date_posted="07-10-2026",
            source="DU Central Portal"
        ),
        VacancyNotice(
            id="test-philosophy-dept-02",
            title="Final List of Adhoc Panel 2025-26",
            college="Department of Philosophy, DU",
            post_type="Ad-hoc Panel Empanelment",
            link="https://philosophy.du.ac.in/userfiles/downloads/adhocpanel/Final%20List%20of%20Adhoc%20Panel%202025-26.pdf",
            pdf_link="https://philosophy.du.ac.in/userfiles/downloads/adhocpanel/Final%20List%20of%20Adhoc%20Panel%202025-26.pdf",
            date_posted="Current Session (2025-26)",
            source="DU Philosophy Department"
        )
    ]

    success = send_email_alert(sample_notices)
    if success:
        print("🎉 SUCCESS! Test email has been sent to", RECIPIENT_EMAIL)
    else:
        print("❌ Could not send email. GMAIL_APP_PASSWORD is not set or invalid.")

if __name__ == "__main__":
    main()
