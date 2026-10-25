"""
Notification module for DU Philosophy Faculty Vacancies.
Features:
  - Deep vacancy details: Category, number of posts, interview date & time, reporting time, venue
  - Verification webpage URL and official PDF download link
  - Automated GitHub Issue alerts
  - Direct HTML email via Gmail SMTP
  - Native macOS banner notifications
"""

import os
import smtplib
import subprocess
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from config import (
    GMAIL_USER,
    GMAIL_APP_PASSWORD,
    RECIPIENT_EMAIL,
    SMTP_SERVER,
    SMTP_PORT
)
from models import VacancyNotice


def send_macos_notification(new_notices: List[VacancyNotice]) -> None:
    """Send native macOS banner notification with sound."""
    if sys.platform != "darwin" or not new_notices:
        return
    try:
        count = len(new_notices)
        first = new_notices[0]
        text = f"{first.college}: {first.vacancies_count} ({first.category}) on {first.interview_date}"
        if count > 1:
            text += f" (+{count - 1} more notices)"
        script = f'display notification "{text}" with title "🏛️ DU Philosophy Vacancy Alert" sound name "Glass"'
        subprocess.run(["osascript", "-e", script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def create_github_issue(new_notices: List[VacancyNotice]) -> bool:
    """Creates an Issue in the GitHub repository for instant email notification."""
    if not new_notices:
        return True

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    count = len(new_notices)
    plural = "ies" if count > 1 else "y"
    issue_title = f"🔔 [DU Alert] {count} New Philosophy Vacanc{plural} / Notice(s) Announced!"

    body_lines = [
        f"## 🏛️ Delhi University Philosophy Vacancy Alert",
        f"**{count} New Vacanc{plural} / Notice(s) Detected with Deep PDF Details!**\n",
        "| College | Posts & Category | Interview Date & Time | Reporting & Venue | Official Links |",
        "|---|---|---|---|---|",
    ]

    for n in new_notices:
        pdf_act = f"[📥 Download PDF]({n.pdf_link})" if n.pdf_link else "N/A"
        web_act = f"[🔗 Verification Page]({n.link})"
        body_lines.append(
            f"| **{n.college}**<br>*{n.post_type}* | **{n.vacancies_count}**<br>Category: `{n.category}` | "
            f"🗓️ **{n.interview_date}** | ⏰ {n.reporting_time}<br>📍 {n.venue} | {pdf_act}<br>{web_act} |"
        )

    body_lines.append("\n---\n*Notification automatically delivered by DU Philosophy Vacancy Tracker bot.*")
    issue_body = "\n".join(body_lines)

    try:
        cmd = ["gh", "issue", "create", "--title", issue_title, "--body", issue_body]
        if repo:
            cmd.extend(["--repo", repo])
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return res.returncode == 0
    except Exception:
        return False


def build_email_content(new_notices: List[VacancyNotice]) -> tuple[str, str]:
    """Builds rich HTML and plain-text email with deep vacancy details."""
    count = len(new_notices)
    plural = "ies" if count > 1 else "y"

    # Plain text version
    text_lines = [
        f"DELHI UNIVERSITY (DU) PHILOSOPHY FACULTY ALERT",
        f"{count} New Philosophy Vacanc{plural} / Notice(s) Detected with Full Details!\n",
        "=" * 65,
    ]

    for idx, n in enumerate(new_notices, 1):
        text_lines.append(f"\n[{idx}] 🏛️ {n.college}")
        text_lines.append(f"Notice Title: {n.title}")
        text_lines.append(f"Post Type: {n.post_type}")
        text_lines.append(f"Vacancies Count: {n.vacancies_count}")
        text_lines.append(f"Reservation Category: {n.category}")
        text_lines.append(f"Interview Date & Time: {n.interview_date}")
        text_lines.append(f"Reporting Time: {n.reporting_time}")
        text_lines.append(f"Venue / Location: {n.venue}")
        text_lines.append(f"Deadline / Submission: {n.deadline or 'Walk-in on Interview Date'}")
        if n.pdf_link:
            text_lines.append(f"Official PDF Download: {n.pdf_link}")
        text_lines.append(f"Verification Page URL: {n.link}")
        text_lines.append("-" * 45)

    text_lines.append("\nThis is an automated 100% free alert from your DU Philosophy GitHub Tracker.")
    plain_text = "\n".join(text_lines)

    # HTML cards with structured key-value grid
    cards_html = []
    for n in new_notices:
        pdf_button = ""
        if n.pdf_link:
            pdf_button = f"""
            <a href="{n.pdf_link}" style="display:inline-block; padding:10px 18px; margin-top:10px; margin-right:10px; background-color:#16a34a; color:#ffffff; text-decoration:none; border-radius:6px; font-weight:700; font-size:13px;">
                📥 Download Official PDF
            </a>
            """

        details_button = f"""
        <a href="{n.link}" style="display:inline-block; padding:10px 18px; margin-top:10px; background-color:#2563eb; color:#ffffff; text-decoration:none; border-radius:6px; font-weight:700; font-size:13px;">
            🔗 Verification Webpage
        </a>
        """

        badge_bg = "#fef3c7"
        badge_color = "#92400e"
        if "guest" in n.post_type.lower():
            badge_bg = "#ede9fe"
            badge_color = "#5b21b6"
        elif "assistant professor" in n.post_type.lower():
            badge_bg = "#dcfce7"
            badge_color = "#166534"

        card = f"""
        <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:12px; padding:20px; margin-bottom:20px; box-shadow:0 2px 4px rgba(0,0,0,0.06);">
            <!-- Card Header -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid #f1f5f9; padding-bottom:10px;">
                <span style="font-size:12px; font-weight:700; background:{badge_bg}; color:{badge_color}; padding:5px 12px; border-radius:20px; text-transform:uppercase;">
                    {n.post_type}
                </span>
                <span style="font-size:12px; color:#475569; font-weight:600;">
                    📅 {n.date_posted or 'Current Session'}
                </span>
            </div>

            <!-- College Title -->
            <h2 style="margin:0 0 6px 0; color:#0f172a; font-size:18px; font-weight:800;">
                🏛️ {n.college}
            </h2>
            <p style="margin:0 0 14px 0; color:#334155; font-size:14px; line-height:1.5;">
                {n.title}
            </p>

            <!-- Detailed Table Information extracted from PDF -->
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:14px; margin-bottom:14px;">
                <table style="width:100%; border-collapse:collapse; font-size:13px;">
                    <tr>
                        <td style="padding:6px 0; color:#64748b; font-weight:600; width:35%;">📌 Vacancy / Posts:</td>
                        <td style="padding:6px 0; color:#0f172a; font-weight:700;">{n.vacancies_count}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 0; color:#64748b; font-weight:600;">🏷️ Category:</td>
                        <td style="padding:6px 0; color:#1e40af; font-weight:700;">{n.category}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 0; color:#64748b; font-weight:600;">🗓️ Interview Date & Time:</td>
                        <td style="padding:6px 0; color:#b91c1c; font-weight:700;">{n.interview_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 0; color:#64748b; font-weight:600;">⏰ Reporting Time:</td>
                        <td style="padding:6px 0; color:#334155;">{n.reporting_time}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 0; color:#64748b; font-weight:600;">📍 Venue / Location:</td>
                        <td style="padding:6px 0; color:#334155; font-weight:500;">{n.venue}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 0; color:#64748b; font-weight:600;">⏳ Deadline / Walk-in:</td>
                        <td style="padding:6px 0; color:#059669; font-weight:600;">{n.deadline or 'Walk-in on Interview Date'}</td>
                    </tr>
                </table>
            </div>

            <!-- Action Buttons -->
            <div>
                {pdf_button}
                {details_button}
            </div>
        </div>
        """
        cards_html.append(card)

    all_cards = "\n".join(cards_html)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>DU Philosophy Vacancy Alert</title>
    </head>
    <body style="font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color:#f1f5f9; margin:0; padding:24px; color:#1e293b;">
        <div style="max-width:680px; margin:0 auto; background:#ffffff; border-radius:14px; overflow:hidden; border:1px solid #cbd5e1; box-shadow:0 10px 15px -3px rgba(0,0,0,0.1);">
            <!-- Header Banner -->
            <div style="background:linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); padding:28px 24px; text-align:center; color:#ffffff;">
                <h1 style="margin:0 0 8px 0; font-size:23px; font-weight:800; letter-spacing:-0.5px;">
                    🏛️ Delhi University Philosophy Vacancy Alert
                </h1>
                <p style="margin:0; font-size:15px; opacity:0.95; font-weight:500;">
                    🔔 {count} New Philosophy Vacanc{plural} / Notice(s) with Full PDF Information!
                </p>
            </div>

            <!-- Body -->
            <div style="padding:24px; background:#f8fafc;">
                <p style="margin:0 0 20px 0; font-size:14px; color:#475569; line-height:1.6;">
                    Hello <strong>Anshu</strong>, here are the latest verified vacancies and walk-in interviews for <strong>Philosophy (दर्शनशास्त्र)</strong> extracted directly from the official Delhi University and college notices:
                </p>

                {all_cards}

                <!-- Important Notes -->
                <div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:14px 18px; border-radius:6px; margin-top:24px;">
                    <h4 style="margin:0 0 6px 0; color:#1e40af; font-size:14px;">💡 Important Instructions for Candidates:</h4>
                    <ul style="margin:0; padding-left:18px; color:#1e3a8a; font-size:12px; line-height:1.6;">
                        <li>Ensure you are registered in the latest <strong>DU Philosophy Ad-hoc Panel</strong> for the session.</li>
                        <li>Carry your complete <strong>Resume / CV</strong>, Original degrees, NET/JRF certificates, and 1 set of self-attested copies.</li>
                        <li>Reach the venue before the specified <strong>Reporting Time</strong>.</li>
                    </ul>
                </div>
            </div>

            <!-- Footer -->
            <div style="background:#f1f5f9; padding:16px 24px; text-align:center; border-top:1px solid #e2e8f0; font-size:12px; color:#64748b;">
                <p style="margin:0 0 4px 0;">
                    Automated 100% Free Notification Bot for <strong>{RECIPIENT_EMAIL}</strong>
                </p>
                <p style="margin:0;">
                    Delhi University Philosophy Faculty Tracker &bull; GitHub Actions 24x7
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return plain_text, html_content


def notify_all(new_notices: List[VacancyNotice]) -> None:
    """Dispatches notifications across all available channels."""
    if not new_notices:
        return

    # 1. Native macOS desktop banner (with sound)
    send_macos_notification(new_notices)

    # 2. Automated GitHub Issue
    create_github_issue(new_notices)

    # 3. Direct Gmail SMTP (if credentials available)
    if GMAIL_USER and GMAIL_APP_PASSWORD:
        send_email_alert(new_notices)


def send_email_alert(new_notices: List[VacancyNotice]) -> bool:
    """Sends email alert for new notices via Gmail SMTP."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return False

    count = len(new_notices)
    plural = "ies" if count > 1 else "y"
    subject = f"🔔 [DU Philosophy Alert] {count} New Vacanc{plural} / Walk-in Interview Notice(s) Announced!"

    plain_body, html_body = build_email_content(new_notices)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"DU Philosophy Vacancy Alert <{GMAIL_USER}>"
    msg["To"] = RECIPIENT_EMAIL

    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, [RECIPIENT_EMAIL], msg.as_string())
        server.quit()
        print(f"[Notifier] ✅ Sent direct email alert with deep PDF details to {RECIPIENT_EMAIL}!")
        return True
    except Exception as e:
        print(f"[Notifier] Error sending email: {e}")
        return False
