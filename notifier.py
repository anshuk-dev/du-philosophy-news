"""
Notification module for DU Philosophy Faculty Vacancies.
Supports:
  1. Automated GitHub Issue alerts (delivers instant email to GitHub user with ZERO password setup)
  2. Direct Gmail SMTP emails (if GMAIL_APP_PASSWORD is set)
  3. Native macOS desktop notifications
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
        text = f"{first.college}: {first.title[:60]}"
        if count > 1:
            text += f" (+{count - 1} more)"
        script = f'display notification "{text}" with title "🏛️ DU Philosophy Vacancy Alert" sound name "Glass"'
        subprocess.run(["osascript", "-e", script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def create_github_issue(new_notices: List[VacancyNotice]) -> bool:
    """
    Creates an Issue in the GitHub repository.
    GitHub automatically sends an instant Email Notification to the user!
    Requires zero external password setup.
    """
    if not new_notices:
        return True

    # Check if gh CLI or GITHUB_TOKEN is available
    github_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY", "")

    count = len(new_notices)
    plural = "ies" if count > 1 else "y"
    issue_title = f"🔔 [DU Alert] {count} New Philosophy Vacanc{plural} / Notice(s)"

    # Build Issue Markdown Body
    body_lines = [
        f"## 🏛️ Delhi University Philosophy Vacancy Alert",
        f"**{count} New Vacanc{plural} / Notice(s) Detected!**\n",
        "| College / Department | Notice Title | Post Type | Date / Deadline | Official Link / PDF |",
        "|---|---|---|---|---|",
    ]

    for n in new_notices:
        pdf_act = f"[📥 Download PDF]({n.pdf_link})" if n.pdf_link else f"[🔗 View Notice]({n.link})"
        body_lines.append(f"| **{n.college}** | {n.title} | `{n.post_type}` | {n.date_posted or 'Current'} | {pdf_act} |")

    body_lines.append("\n---\n*Notification automatically delivered by DU Philosophy Vacancy Tracker bot.*")
    issue_body = "\n".join(body_lines)

    try:
        # Try via gh CLI
        cmd = ["gh", "issue", "create", "--title", issue_title, "--body", issue_body]
        if repo:
            cmd.extend(["--repo", repo])

        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode == 0:
            print(f"[Notifier] ✅ Created GitHub Issue alert: {res.stdout.strip()}")
            return True
        else:
            # If repo is not yet set or gh failed, continue silently
            return False
    except Exception:
        return False


def build_email_content(new_notices: List[VacancyNotice]) -> tuple[str, str]:
    """Builds both HTML and plain-text email bodies for the notices."""
    count = len(new_notices)
    plural = "ies" if count > 1 else "y"

    text_lines = [
        f"DELHI UNIVERSITY (DU) PHILOSOPHY FACULTY ALERT",
        f"{count} New Philosophy Vacanc{plural} / Notice(s) Detected!\n",
        "=" * 60,
    ]

    for idx, n in enumerate(new_notices, 1):
        text_lines.append(f"\n[{idx}] {n.college}")
        text_lines.append(f"Post Type: {n.post_type}")
        text_lines.append(f"Title: {n.title}")
        text_lines.append(f"Date/Session: {n.date_posted or 'Current'}")
        if n.pdf_link:
            text_lines.append(f"Official PDF: {n.pdf_link}")
        text_lines.append(f"Notice Link: {n.link}")
        text_lines.append("-" * 40)

    text_lines.append("\nThis is an automated 100% free alert from your DU Philosophy GitHub Tracker.")
    plain_text = "\n".join(text_lines)

    cards_html = []
    for n in new_notices:
        pdf_button = ""
        if n.pdf_link:
            pdf_button = f"""
            <a href="{n.pdf_link}" style="display:inline-block; padding:8px 16px; margin-top:8px; margin-right:8px; background-color:#16a34a; color:#ffffff; text-decoration:none; border-radius:6px; font-weight:600; font-size:13px;">
                📥 Download Official Notice PDF
            </a>
            """

        details_button = f"""
        <a href="{n.link}" style="display:inline-block; padding:8px 16px; margin-top:8px; background-color:#2563eb; color:#ffffff; text-decoration:none; border-radius:6px; font-weight:600; font-size:13px;">
            🔗 View Announcement / Portal
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
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:18px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-size:12px; font-weight:700; background:{badge_bg}; color:{badge_color}; padding:4px 10px; border-radius:20px; text-transform:uppercase;">
                    {n.post_type}
                </span>
                <span style="font-size:12px; color:#64748b; font-weight:500;">
                    📅 {n.date_posted or 'Current Session'}
                </span>
            </div>
            <h3 style="margin:0 0 6px 0; color:#0f172a; font-size:16px; font-weight:700;">
                🏛️ {n.college}
            </h3>
            <p style="margin:0 0 12px 0; color:#334155; font-size:14px; line-height:1.5;">
                {n.title}
            </p>
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
    <body style="font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color:#f8fafc; margin:0; padding:24px; color:#1e293b;">
        <div style="max-width:640px; margin:0 auto; background:#ffffff; border-radius:14px; overflow:hidden; border:1px solid #e2e8f0; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
            <div style="background:linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding:28px 24px; text-align:center; color:#ffffff;">
                <h1 style="margin:0 0 8px 0; font-size:22px; font-weight:800; letter-spacing:-0.5px;">
                    🏛️ Delhi University Philosophy Alert
                </h1>
                <p style="margin:0; font-size:15px; opacity:0.95; font-weight:500;">
                    🔔 {count} New Vacanc{plural} / Notice(s) Detected!
                </p>
            </div>

            <div style="padding:24px; background:#f8fafc;">
                <p style="margin:0 0 18px 0; font-size:14px; color:#475569;">
                    Hello Anshu, new notices matching <strong>Philosophy</strong> (Guest Faculty / Assistant Professor / Ad-hoc Panel) have just been published across DU colleges/departments:
                </p>

                {all_cards}

                <div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:12px 16px; border-radius:4px; margin-top:20px;">
                    <p style="margin:0; font-size:12px; color:#1e40af;">
                        💡 <strong>Tip:</strong> Keep your documents, NET/JRF certificate, and DU Ad-hoc panel registration ready. For walk-in interviews, reach the college before reporting time.
                    </p>
                </div>
            </div>

            <div style="background:#f1f5f9; padding:16px 24px; text-align:center; border-top:1px solid #e2e8f0; font-size:12px; color:#64748b;">
                <p style="margin:0 0 4px 0;">
                    Automated 100% Free Notification Bot for <strong>{RECIPIENT_EMAIL}</strong>
                </p>
                <p style="margin:0;">
                    Delhi University Philosophy Faculty Tracker
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

    # 2. Automated GitHub Issue (triggers email to GitHub user without passwords)
    create_github_issue(new_notices)

    # 3. Direct Gmail SMTP (if credentials available)
    if GMAIL_USER and GMAIL_APP_PASSWORD:
        send_email_alert(new_notices)
    else:
        # Write to GitHub Actions summary if running in CI
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path and os.path.exists(os.path.dirname(summary_path)):
            try:
                count = len(new_notices)
                with open(summary_path, "a", encoding="utf-8") as f:
                    f.write(f"### 🔔 {count} New DU Philosophy Notice(s) Detected!\n\n")
                    for n in new_notices:
                        f.write(f"- **{n.college}** (`{n.post_type}`): [{n.title}]({n.link})")
                        if n.pdf_link:
                            f.write(f" — [Download PDF]({n.pdf_link})")
                        f.write("\n")
            except Exception:
                pass


def send_email_alert(new_notices: List[VacancyNotice]) -> bool:
    """Sends email alert for new notices via Gmail SMTP."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return False

    count = len(new_notices)
    plural = "ies" if count > 1 else "y"
    subject = f"🔔 [DU Alert] {count} New Philosophy Vacanc{plural} / Notice(s) Announced!"

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
        print(f"[Notifier] ✅ Sent direct email alert to {RECIPIENT_EMAIL}!")
        return True
    except Exception as e:
        print(f"[Notifier] Error sending email: {e}")
        return False
