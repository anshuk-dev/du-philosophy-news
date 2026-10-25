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
from datetime import datetime
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
    """
    Builds an authoritative Academic Gazette & Recruitment Bulletin email.
    Designed in the tradition of premier university gazettes (Oxford/UChicago/DU),
    with table-based bulletproof rendering for flawless display in Gmail, Apple Mail, and Outlook.
    """
    count = len(new_notices)
    plural = "ies" if count > 1 else "y"

    # 1. Plain Text Version
    text_lines = [
        "=================================================================",
        "   DELHI UNIVERSITY (DU) — PHILOSOPHY FACULTY RECRUITMENT GAZETTE",
        "         Official Walk-in & Vacancy Notification Dispatch",
        "=================================================================",
        f"Edition: {datetime.now().strftime('%d %B %Y')} | {count} Verified Vacanc{plural}\n",
    ]

    for idx, n in enumerate(new_notices, 1):
        text_lines.append(f"[{idx}] 🏛️ {n.college.upper()}")
        text_lines.append(f"    Post Type       : {n.post_type}")
        text_lines.append(f"    Notice Title    : {n.title}")
        text_lines.append(f"    Vacancies       : {n.vacancies_count}")
        text_lines.append(f"    Category Matrix : {n.category}")
        text_lines.append(f"    Interview Date  : {n.interview_date}")
        text_lines.append(f"    Reporting Time  : {n.reporting_time}")
        text_lines.append(f"    Venue / Room    : {n.venue}")
        text_lines.append(f"    Deadline        : {n.deadline or 'Walk-in on Interview Date'}")
        if n.pdf_link:
            text_lines.append(f"    Official PDF    : {n.pdf_link}")
        text_lines.append(f"    Portal Link     : {n.link}")
        text_lines.append("-" * 65)

    text_lines.append("\nCandidate Guidelines:")
    text_lines.append("1. Candidate must be empanelled in the latest DU Philosophy Ad-hoc Panel.")
    text_lines.append("2. Carry complete CV, original certificates, NET/JRF awards, and self-attested photocopies.")
    text_lines.append("3. Report 30 minutes prior to scheduled reporting time.")
    text_lines.append(f"\nDelivered automatically to {RECIPIENT_EMAIL} by DU Philosophy Vacancy Tracker.")
    plain_text = "\n".join(text_lines)

    # 2. Academic Gazette HTML Cards
    cards_html = []
    for idx, n in enumerate(new_notices, 1):
        # Color coding badges based on post type
        post_lower = n.post_type.lower()
        if "walk-in" in post_lower or "interview" in post_lower:
            badge_bg = "#fef2f2"
            badge_border = "#fecaca"
            badge_color = "#991b1b"
            accent_bar = "#b91c1c"
            badge_icon = "⚡ WALK-IN INTERVIEW"
        elif "guest" in post_lower:
            badge_bg = "#eff6ff"
            badge_border = "#bfdbfe"
            badge_color = "#1e40af"
            accent_bar = "#2563eb"
            badge_icon = "🎓 GUEST FACULTY"
        elif "assistant" in post_lower or "permanent" in post_lower:
            badge_bg = "#f0fdf4"
            badge_border = "#bbf7d0"
            badge_color = "#166534"
            accent_bar = "#16a34a"
            badge_icon = "🏛️ ASSISTANT PROFESSOR"
        else:
            badge_bg = "#fefce8"
            badge_border = "#fef08a"
            badge_color = "#854d0e"
            accent_bar = "#d97706"
            badge_icon = f"📢 {n.post_type.upper()}"

        # PDF Action Button
        pdf_button_html = ""
        if n.pdf_link:
            pdf_button_html = f"""
            <td style="padding-right: 10px;">
                <table border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="center" style="border-radius: 6px; background-color: #991b1b;">
                            <a href="{n.pdf_link}" target="_blank" style="display: inline-block; padding: 9px 18px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 700; color: #ffffff; text-decoration: none; border-radius: 6px;">
                                📥 Download Official PDF Notice &rarr;
                            </a>
                        </td>
                    </tr>
                </table>
            </td>
            """

        portal_button_html = f"""
        <td>
            <table border="0" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center" style="border-radius: 6px; background-color: #0f172a;">
                        <a href="{n.link}" target="_blank" style="display: inline-block; padding: 9px 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 6px;">
                            🔗 College Verification Page &nearr;
                        </a>
                    </td>
                </tr>
            </table>
        </td>
        """

        card = f"""
        <!-- NOTICE CARD {idx} -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #ffffff; border: 1px solid #e2e8f0; border-top: 4px solid {accent_bar}; border-radius: 8px; margin-bottom: 22px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
            <tr>
                <td style="padding: 22px 24px;">
                    
                    <!-- Card Header: College & Badges -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 12px; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px;">
                        <tr>
                            <td align="left" style="vertical-align: middle;">
                                <span style="font-size: 11px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px;">
                                    College / Institution
                                </span>
                                <h2 style="margin: 3px 0 0 0; font-family: Georgia, 'Times New Roman', serif; font-size: 21px; font-weight: 700; color: #0f172a; letter-spacing: -0.3px;">
                                    🏛️ {n.college}
                                </h2>
                            </td>
                            <td align="right" style="vertical-align: top;">
                                <span style="display: inline-block; background-color: {badge_bg}; border: 1px solid {badge_border}; color: {badge_color}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; font-weight: 800; padding: 5px 12px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px;">
                                    {badge_icon}
                                </span>
                            </td>
                        </tr>
                    </table>

                    <!-- Notice Title -->
                    <p style="margin: 0 0 16px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14.5px; font-weight: 600; color: #334155; line-height: 1.5;">
                        {n.title}
                    </p>

                    <!-- Academic Data Matrix (Structured Table) -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 18px;">
                        <tr>
                            <td style="padding: 12px 16px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13.5px;">
                                    <tr>
                                        <td width="35%" style="padding: 6px 0; color: #64748b; font-weight: 600;">
                                            👥 Vacancies & Posts:
                                        </td>
                                        <td style="padding: 6px 0; color: #0f172a; font-weight: 800; font-size: 14px;">
                                            {n.vacancies_count}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 6px 0; color: #64748b; font-weight: 600;">
                                            🏷️ Category Matrix:
                                        </td>
                                        <td style="padding: 6px 0;">
                                            <span style="display: inline-block; background-color: #ede9fe; color: #5b21b6; font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: 12.5px;">
                                                {n.category}
                                            </span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 6px 0; color: #64748b; font-weight: 600;">
                                            🗓️ Walk-in Date & Time:
                                        </td>
                                        <td style="padding: 6px 0;">
                                            <span style="display: inline-block; background-color: #fef2f2; border: 1px solid #fecaca; color: #991b1b; font-weight: 800; padding: 3px 10px; border-radius: 4px; font-size: 13.5px;">
                                                {n.interview_date}
                                            </span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 6px 0; color: #64748b; font-weight: 600;">
                                            ⏰ Reporting Time:
                                        </td>
                                        <td style="padding: 6px 0; color: #1e293b; font-weight: 600;">
                                            {n.reporting_time}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 6px 0; color: #64748b; font-weight: 600;">
                                            📍 Venue / Room:
                                        </td>
                                        <td style="padding: 6px 0; color: #334155; font-weight: 500;">
                                            {n.venue}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 6px 0; color: #64748b; font-weight: 600;">
                                            ⏳ Mode / Deadline:
                                        </td>
                                        <td style="padding: 6px 0; color: #047857; font-weight: 700;">
                                            {n.deadline or 'Walk-in (Bring Original Documents)'}
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>

                    <!-- Buttons Row -->
                    <table border="0" cellpadding="0" cellspacing="0">
                        <tr>
                            {pdf_button_html}
                            {portal_button_html}
                        </tr>
                    </table>

                </td>
            </tr>
        </table>
        """
        cards_html.append(card)

    all_cards = "\n".join(cards_html)
    today_date = datetime.now().strftime("%A, %d %B %Y")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Delhi University Philosophy Faculty Bulletin</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">

    <!-- Hidden Preheader for Inbox Preview -->
    <div style="display: none; font-size: 1px; color: #f1f5f9; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all;">
        DU Faculty Bulletin: {count} new verified Philosophy walk-in interview notice(s) announced. Dates, venues, seat matrix & official PDF download links inside.
    </div>

    <!-- Outer Wrapper -->
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f1f5f9; padding: 25px 0;">
        <tr>
            <td align="center">

                <!-- Main Container (640px) -->
                <table border="0" cellpadding="0" cellspacing="0" width="640" style="max-width: 640px; width: 100%; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08);">
                    
                    <!-- TOP UNIVERSITY HEADER (Academic Gazette Styling) -->
                    <tr>
                        <td style="background-color: #881337; background: linear-gradient(135deg, #701a28 0%, #881337 50%, #991b1b 100%); padding: 32px 30px; text-align: center; border-bottom: 4px solid #d97706;">
                            
                            <!-- University Masthead -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center">
                                        <span style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11.5px; font-weight: 800; color: #fde68a; letter-spacing: 2px; text-transform: uppercase;">
                                            UNIVERSITY OF DELHI &bull; DEPARTMENT OF PHILOSOPHY
                                        </span>
                                        <h1 style="margin: 8px 0 6px 0; font-family: Georgia, 'Times New Roman', serif; font-size: 25px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px; line-height: 1.25;">
                                            Faculty Recruitment Gazette
                                        </h1>
                                        <p style="margin: 0 0 14px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13.5px; color: #fecdd3; font-weight: 500;">
                                            Official Walk-In Interviews & Vacancy Dispatch for Philosophy (दर्शनशास्त्र)
                                        </p>
                                        <span style="display: inline-block; background-color: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.25); color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11.5px; font-weight: 700; padding: 4px 14px; border-radius: 20px; letter-spacing: 0.5px;">
                                            📅 {today_date} &bull; {count} Active Notice(s)
                                        </span>
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>

                    <!-- SUMMARY STATS RIBBON -->
                    <tr>
                        <td style="background-color: #0f172a; padding: 12px 24px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; color: #94a3b8;">
                                        ⚡ <strong style="color: #ffffff;">STATUS:</strong> Strictly Ongoing & Upcoming
                                        &nbsp;&bull;&nbsp;
                                        🏛️ <strong style="color: #ffffff;">SUBJECT:</strong> Philosophy
                                        &nbsp;&bull;&nbsp;
                                        📑 <strong style="color: #38bdf8;">DEEP PDF OCR:</strong> Extracted
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- MAIN CONTENT BODY -->
                    <tr>
                        <td style="padding: 26px 28px; background-color: #f8fafc;">
                            
                            <p style="margin: 0 0 20px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14.5px; color: #334155; line-height: 1.6;">
                                Respected <strong>Candidate / Faculty Aspirant</strong>,<br>
                                Below are the latest verified vacancies and walk-in interviews for <strong>Philosophy</strong> across Delhi University colleges. All details (interview dates, venues, category allocations, and application modes) have been verified directly against official university portals and notification PDFs:
                            </p>

                            <!-- CARDS INJECTION -->
                            {all_cards}

                            <!-- CANDIDATE INSTRUCTIONS BOX -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-left: 5px solid #2563eb; border-radius: 6px; margin-top: 10px;">
                                <tr>
                                    <td style="padding: 18px 20px;">
                                        <h3 style="margin: 0 0 8px 0; font-family: Georgia, 'Times New Roman', serif; font-size: 16px; color: #1e40af; font-weight: 700;">
                                            📋 Mandatory Walk-in Candidate Checklist
                                        </h3>
                                        <ul style="margin: 0; padding-left: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; color: #1e3a8a; line-height: 1.6;">
                                            <li style="margin-bottom: 5px;">
                                                <strong>Ad-hoc Panel Eligibility:</strong> Ensure your name is empanelled in the latest official <strong>DU Philosophy Ad-hoc Panel</strong> for the current session.
                                            </li>
                                            <li style="margin-bottom: 5px;">
                                                <strong>Dossier to Carry:</strong> Bring your updated <strong>Curriculum Vitae (CV)</strong>, original degrees, marksheets, NET/JRF certificates, and 1 set of self-attested photocopies.
                                            </li>
                                            <li style="margin-bottom: 5px;">
                                                <strong>Category Proof:</strong> If applying under reserved categories (OBC-NCL, SC, ST, EWS, PwD), bring a valid certificate issued in the prescribed central format.
                                            </li>
                                            <li>
                                                <strong>Reporting Protocol:</strong> Report at the specified venue at least <strong>30 minutes</strong> before the scheduled time. No TA/DA is provided by the university.
                                            </li>
                                        </ul>
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>

                    <!-- INSTITUTIONAL FOOTER -->
                    <tr>
                        <td style="background-color: #0f172a; padding: 24px 30px; text-align: center; border-top: 1px solid #1e293b;">
                            <p style="margin: 0 0 6px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 600; color: #e2e8f0;">
                                Delhi University Philosophy Faculty Automated Monitoring Gazette
                            </p>
                            <p style="margin: 0 0 10px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                                Automated 24x7 Cloud Dispatch &bull; Delivered to <strong style="color: #38bdf8;">{RECIPIENT_EMAIL}</strong><br>
                                Powered by GitHub Actions Cloud &bull; Scanned via PyMuPDF & Tesseract OCR
                            </p>
                            <p style="margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; color: #64748b;">
                                University of Delhi &bull; Department of Philosophy &bull; Faculty of Arts &bull; New Delhi 110007
                            </p>
                        </td>
                    </tr>

                </table><!-- /Main Container -->

            </td>
        </tr>
    </table><!-- /Outer Wrapper -->

</body>
</html>
"""

    return plain_text, html_content

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
