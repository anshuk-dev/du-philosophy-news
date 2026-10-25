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
    Builds a high-end, minimalist Editorial Academic Broadsheet newsletter.
    Inspired by Adobe Express and Canva editorial publication templates (Playfair/Bodoni
    high-contrast serif, restrained warm-stone palette, hairline grid rules, and generous whitespace).
    Uses strict table-based architecture for bulletproof rendering in Gmail, Outlook, and Apple Mail.
    """
    count = len(new_notices)
    plural = "ies" if count > 1 else "y"
    today_date = datetime.now().strftime("%d %B %Y").upper()

    # 1. Plain Text Version
    text_lines = [
        "=================================================================",
        "                 THE DU PHILOSOPHY GAZETTE",
        "        Official Faculty Recruitment & Walk-in Dispatch",
        "=================================================================",
        f"EDITION: {today_date}  |  {count} VERIFIED VACANC{plural.upper()}\n",
    ]

    for idx, n in enumerate(new_notices, 1):
        text_lines.append(f"[{idx:02d}] {n.college.upper()}")
        text_lines.append(f"     TYPE      : {n.post_type}")
        text_lines.append(f"     NOTICE    : {n.title}")
        text_lines.append(f"     SEATS     : {n.vacancies_count} ({n.category})")
        text_lines.append(f"     INTERVIEW : {n.interview_date}")
        text_lines.append(f"     REPORTING : {n.reporting_time}")
        text_lines.append(f"     VENUE     : {n.venue}")
        text_lines.append(f"     MODE      : {n.deadline or 'Walk-in on Interview Date'}")
        if n.pdf_link:
            text_lines.append(f"     PDF LINK  : {n.pdf_link}")
        text_lines.append(f"     PORTAL    : {n.link}")
        text_lines.append("-" * 65)

    text_lines.append("\nCANDIDATE PROTOCOL:")
    text_lines.append("01. Empanelled in the current DU Philosophy Ad-hoc Panel.")
    text_lines.append("02. Carry updated CV, degrees, NET/JRF certificates, and 1 set of self-attested copies.")
    text_lines.append("03. Report 30 minutes prior to scheduled reporting time.")
    text_lines.append(f"\nDispatched to {RECIPIENT_EMAIL} by DU Philosophy Automated Gazette.")
    plain_text = "\n".join(text_lines)

    # 2. Editorial HTML Cards
    cards_html = []
    for idx, n in enumerate(new_notices, 1):
        # Action Buttons (Canva/Adobe Minimalist Solid + Ghost Buttons)
        pdf_button_html = ""
        if n.pdf_link:
            pdf_button_html = f"""
            <td style="padding-right: 12px;">
                <table border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="center" style="background-color: #1c1917; border-radius: 2px;">
                            <a href="{n.pdf_link}" target="_blank" style="display: inline-block; padding: 10px 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; font-weight: 700; color: #ffffff; text-decoration: none; text-transform: uppercase; letter-spacing: 1.5px;">
                                Download Notice (PDF) &rarr;
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
                    <td align="center" style="background-color: transparent; border: 1px solid #1c1917; border-radius: 2px;">
                        <a href="{n.link}" target="_blank" style="display: inline-block; padding: 9px 18px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; font-weight: 700; color: #1c1917; text-decoration: none; text-transform: uppercase; letter-spacing: 1.5px;">
                            Verification Portal &nearr;
                        </a>
                    </td>
                </tr>
            </table>
        </td>
        """

        card = f"""
        <!-- EDITORIAL NOTICE ITEM {idx:02d} -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #ffffff; border: 1px solid #e7e5e0; border-radius: 4px; margin-bottom: 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <tr>
                <td style="padding: 26px 28px;">
                    
                    <!-- Kicker & Metadata Bar -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 10px;">
                        <tr>
                            <td align="left">
                                <span style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10.5px; font-weight: 700; color: #701a28; letter-spacing: 2px; text-transform: uppercase;">
                                    DISPATCH #{idx:02d} &bull; {n.post_type}
                                </span>
                            </td>
                            <td align="right">
                                <span style="display: inline-block; border: 1px solid #d6d3d1; background-color: #faf9f5; color: #44403c; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 2px; text-transform: uppercase; letter-spacing: 1px;">
                                    VERIFIED NOTICE
                                </span>
                            </td>
                        </tr>
                    </table>

                    <!-- College Display Title (Editorial Serif) -->
                    <h2 style="margin: 0 0 8px 0; font-family: 'Playfair Display', 'Bodoni MT', 'Didot', Georgia, serif; font-size: 24px; font-weight: 700; color: #1c1917; letter-spacing: -0.4px; line-height: 1.25;">
                        {n.college}
                    </h2>

                    <!-- Notice Title -->
                    <p style="margin: 0 0 18px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; color: #57534e; line-height: 1.6;">
                        {n.title}
                    </p>

                    <!-- Editorial Specification Grid (Hairline Separators) -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top: 1px solid #e7e5e0; border-bottom: 1px solid #e7e5e0; padding: 14px 0; margin-bottom: 20px;">
                        <tr>
                            <td>
                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px;">
                                    <tr>
                                        <td width="35%" style="padding: 5px 0; color: #78716c; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                                            Positions & Seats:
                                        </td>
                                        <td style="padding: 5px 0; color: #1c1917; font-weight: 700;">
                                            {n.vacancies_count}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; color: #78716c; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                                            Category Matrix:
                                        </td>
                                        <td style="padding: 5px 0; color: #1c1917; font-weight: 600;">
                                            {n.category}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; color: #78716c; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                                            Walk-in Date & Time:
                                        </td>
                                        <td style="padding: 5px 0; color: #701a28; font-weight: 800; font-size: 14px;">
                                            {n.interview_date}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; color: #78716c; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                                            Reporting Time:
                                        </td>
                                        <td style="padding: 5px 0; color: #292524; font-weight: 600;">
                                            {n.reporting_time}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; color: #78716c; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                                            Venue / Location:
                                        </td>
                                        <td style="padding: 5px 0; color: #44403c;">
                                            {n.venue}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; color: #78716c; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                                            Mode / Deadline:
                                        </td>
                                        <td style="padding: 5px 0; color: #1c1917; font-weight: 600;">
                                            {n.deadline or 'Walk-in (Bring Original Dossier)'}
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

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The DU Philosophy Gazette</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f7f6f2; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">

    <!-- Hidden Preheader for Inbox Preview -->
    <div style="display: none; font-size: 1px; color: #f7f6f2; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all;">
        DU Philosophy Gazette: {count} verified walk-in vacancy dispatch(es) announced across colleges. Full schedule, seat matrix & PDF notices.
    </div>

    <!-- Outer Wrapper -->
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f7f6f2; padding: 36px 0;">
        <tr>
            <td align="center">

                <!-- Main Container (640px) -->
                <table border="0" cellpadding="0" cellspacing="0" width="640" style="max-width: 640px; width: 100%; background-color: #ffffff; border: 1px solid #e7e5e0; box-shadow: 0 4px 20px -2px rgba(0,0,0,0.03);">
                    
                    <!-- EDITORIAL MASTHEAD (Adobe & Canva Magazine Broadsheet) -->
                    <tr>
                        <td style="padding: 34px 34px 24px 34px; background-color: #ffffff;">
                            
                            <!-- Overline / University Header -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 14px;">
                                <tr>
                                    <td align="left">
                                        <span style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10px; font-weight: 800; color: #78716c; letter-spacing: 2.5px; text-transform: uppercase;">
                                            UNIVERSITY OF DELHI &bull; DEPT. OF PHILOSOPHY
                                        </span>
                                    </td>
                                    <td align="right">
                                        <span style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10px; font-weight: 700; color: #a8a29e; letter-spacing: 1.5px; text-transform: uppercase;">
                                            VOL. XXIV // NO. 10
                                        </span>
                                    </td>
                                </tr>
                            </table>

                            <!-- Hairline Accent Divider -->
                            <div style="height: 1px; background-color: #1c1917; margin-bottom: 18px;"></div>

                            <!-- Publication Title (Playfair Display / Serif) -->
                            <h1 style="margin: 0 0 6px 0; font-family: 'Playfair Display', 'Bodoni MT', 'Didot', Georgia, serif; font-size: 34px; font-weight: 700; color: #1c1917; letter-spacing: -0.8px; line-height: 1.15;">
                                The Philosophy Gazette
                            </h1>

                            <!-- Subhead -->
                            <p style="margin: 0 0 16px 0; font-family: 'Playfair Display', Georgia, serif; font-size: 15px; font-style: italic; color: #78716c; line-height: 1.4;">
                                Official Faculty Recruitment Dispatches & Walk-in Interview Bulletins
                            </p>

                            <!-- Issue Metadata Strip -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top: 1px solid #e7e5e0; border-bottom: 1px solid #e7e5e0; padding: 8px 0;">
                                <tr>
                                    <td align="left" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10.5px; font-weight: 700; color: #78716c; letter-spacing: 1px; text-transform: uppercase;">
                                        DATE: {today_date} &nbsp;&bull;&nbsp; DISPATCHES: {count} ACTIVE &nbsp;&bull;&nbsp; STATUS: ONGOING & UPCOMING
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>

                    <!-- EDITORIAL BODY CANVAS -->
                    <tr>
                        <td style="padding: 10px 34px 28px 34px; background-color: #fcfbf9;">
                            
                            <p style="margin: 16px 0 24px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14.5px; color: #44403c; line-height: 1.65;">
                                Dear <strong>Candidate</strong>,<br>
                                Below are the latest verified faculty vacancy dispatches and walk-in interview schedules for <strong>Philosophy (दर्शनशास्त्र)</strong> across Delhi University colleges. All notices are extracted directly from official notification registries:
                            </p>

                            <!-- CARDS INJECTION -->
                            {all_cards}

                            <!-- CANDIDATE PROTOCOL MEMO (Canva Editorial Style) -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #faf9f5; border: 1px solid #e7e5e0; border-radius: 4px; margin-top: 10px;">
                                <tr>
                                    <td style="padding: 24px 26px;">
                                        <span style="display: block; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10.5px; font-weight: 800; color: #701a28; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px;">
                                            MANDATORY CANDIDATE PROTOCOL
                                        </span>
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; color: #44403c; line-height: 1.6;">
                                            <tr>
                                                <td style="padding-bottom: 8px; vertical-align: top; width: 28px; font-weight: 700; color: #78716c;">01.</td>
                                                <td style="padding-bottom: 8px;">
                                                    <strong>Ad-hoc Panel Registration:</strong> Candidates must be empanelled in the latest official <strong>DU Philosophy Ad-hoc Panel</strong> for the current academic session.
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-bottom: 8px; vertical-align: top; width: 28px; font-weight: 700; color: #78716c;">02.</td>
                                                <td style="padding-bottom: 8px;">
                                                    <strong>Dossier Requirements:</strong> Carry your updated CV, original marksheets, degree certificates, NET/JRF certificates, and 1 set of self-attested photocopies.
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-bottom: 8px; vertical-align: top; width: 28px; font-weight: 700; color: #78716c;">03.</td>
                                                <td style="padding-bottom: 8px;">
                                                    <strong>Category Verification:</strong> Reserved category applicants (OBC-NCL, SC, ST, EWS) must present valid certificates in the prescribed central format.
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="vertical-align: top; width: 28px; font-weight: 700; color: #78716c;">04.</td>
                                                <td>
                                                    <strong>Reporting Protocol:</strong> Report to the specified venue at least <strong>30 minutes</strong> prior to the designated reporting time.
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>

                    <!-- EDITORIAL COLOPHON / FOOTER -->
                    <tr>
                        <td style="padding: 26px 34px; background-color: #ffffff; border-top: 1px solid #1c1917; text-align: left;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="left">
                                        <span style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10px; font-weight: 800; color: #1c1917; letter-spacing: 2px; text-transform: uppercase; display: block; margin-bottom: 4px;">
                                            THE DU PHILOSOPHY GAZETTE // AUTONOMOUS MONITOR
                                        </span>
                                        <p style="margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11.5px; color: #78716c; line-height: 1.5;">
                                            Dispatched to <strong style="color: #1c1917;">{RECIPIENT_EMAIL}</strong> &bull; Powered by GitHub Actions Cloud 24/7<br>
                                            Faculty of Arts &bull; University of Delhi &bull; New Delhi 110007
                                        </p>
                                    </td>
                                    <td align="right" style="vertical-align: middle;">
                                        <span style="font-family: 'Playfair Display', Georgia, serif; font-size: 18px; font-style: italic; color: #a8a29e;">
                                            Du.ac.in
                                        </span>
                                    </td>
                                </tr>
                            </table>
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
