"""
Quick Test Mailer Script with Deep PDF Details.
Sends a sample DU Philosophy Vacancy Alert email to anshu.philosophy@gmail.com.
"""

from config import RECIPIENT_EMAIL
from models import VacancyNotice
from notifier import send_email_alert

def main():
    print("=" * 65)
    print("🧪 Sending Test Email with Deep PDF Details to:", RECIPIENT_EMAIL)
    print("=" * 65)

    sample_notices = [
        VacancyNotice(
            id="ramjas-phil-01",
            title="Advertisement for the Post of Guest faculty in the Department of Philosophy - Ramjas College",
            college="Ramjas College",
            post_type="Guest Faculty (Walk-in / Interview)",
            link="https://www.du.ac.in/index.php?mact=News,cntnt01,detail,0&cntnt01articleid=18956&cntnt01returnid=219",
            pdf_link="https://www.du.ac.in/uploads/new-web/07102026-ramjas-guest-philosophy.pdf",
            date_posted="07-10-2026",
            source="DU Central Portal",
            vacancies_count="01 Post (Leave Vacancy)",
            category="EWS (Economically Weaker Section)",
            interview_date="14.10.2026 (Wednesday) at 02:15 P.M.",
            reporting_time="01:00 P.M. to 01:55 P.M.",
            venue="Office of the Principal, Ramjas College, University Enclave, Delhi — 110007",
            deadline="Walk-in Interview"
        ),
        VacancyNotice(
            id="lsr-phil-02",
            title="Advertisement for the post of Assistant Professor on Guest Basis in the Department of Philosophy - Lady Shri Ram College",
            college="Lady Shri Ram College for Women (LSR)",
            post_type="Guest Faculty (Walk-in / Interview)",
            link="https://www.du.ac.in/index.php?mact=News,cntnt01,detail,0&cntnt01articleid=18535&cntnt01returnid=219",
            pdf_link="https://www.du.ac.in/uploads/2026/17082026-lady-shri-Advt-Guest-fac-Philosophy%20Department_compressed.pdf",
            date_posted="17-08-2026",
            source="DU Central Portal",
            vacancies_count="02 Posts",
            category="UR (Unreserved / General)",
            interview_date="25.08.2026 (Tuesday) at 11:00 A.M.",
            reporting_time="Report 30 mins before interview",
            venue="Office of the Principal, Lady Shri Ram College for Women, Lajpat Nagar IV, New Delhi",
            deadline="Walk-in Interview (Minimum API 55)"
        ),
        VacancyNotice(
            id="gargi-phil-03",
            title="Corrigendum: Walk-in Interview for Guest Faculty in Department of Philosophy - Gargi College",
            college="Gargi College",
            post_type="Guest Faculty (Walk-in / Interview)",
            link="https://www.du.ac.in/index.php?mact=News,cntnt01,detail,0&cntnt01articleid=18479&cntnt01returnid=219",
            pdf_link="https://www.du.ac.in/uploads/2026/12082026-gargi-Guest%20appointment%20PHI-26-27-Corrigendum.pdf",
            date_posted="12-08-2026",
            source="DU Central Portal",
            vacancies_count="01 Post",
            category="SC (Scheduled Caste)",
            interview_date="21.08.2026 at 11:00 A.M.",
            reporting_time="Report 30 minutes before scheduled time",
            venue="Gargi College, Siri Fort Road, New Delhi – 110049",
            deadline="Walk-in Interview"
        ),
        VacancyNotice(
            id="hindu-phil-04",
            title="Interview for the appointment of Assistant Professor/s on Guest basis in the Department of Philosophy - Hindu College",
            college="Hindu College",
            post_type="Guest Faculty (Walk-in / Interview)",
            link="https://www.du.ac.in/index.php?mact=News,cntnt01,detail,0&cntnt01articleid=18134&cntnt01returnid=219",
            pdf_link="https://www.du.ac.in/uploads/2026/08092027_Hindu.pdf",
            date_posted="Current Session (2025-26 / 2026-27)",
            source="DU Central Portal",
            vacancies_count="01+ Post(s)",
            category="All Categories (UR/SC/ST/OBC/EWS)",
            interview_date="14.07.2026 (Tuesday) at 3:00 P.M.",
            reporting_time="Report 30 mins before interview",
            venue="Office of the Principal, Hindu College, University of Delhi, Delhi — 110007",
            deadline="Walk-in Interview"
        ),
        VacancyNotice(
            id="dept-phil-05",
            title="Final List of Adhoc Panel 2025-26 - Department of Philosophy",
            college="Department of Philosophy, DU",
            post_type="Ad-hoc Panel Empanelment",
            link="https://philosophy.du.ac.in/userfiles/downloads/adhocpanel/Final%20List%20of%20Adhoc%20Panel%202025-26.pdf",
            pdf_link="https://philosophy.du.ac.in/userfiles/downloads/adhocpanel/Final%20List%20of%20Adhoc%20Panel%202025-26.pdf",
            date_posted="Current Session (2025-26)",
            source="DU Philosophy Department Portal",
            vacancies_count="Department Panel List",
            category="Category I to VII (Approved Candidates)",
            interview_date="Active Panel for 2025-26 College Appointments",
            reporting_time="Official DU Empanelment List",
            venue="Faculty of Arts, North Campus, University of Delhi",
            deadline="Valid for entire Academic Year 2025-26"
        )
    ]

    success = send_email_alert(sample_notices)
    if success:
        print("🎉 SUCCESS! Detailed email has been delivered to", RECIPIENT_EMAIL)
    else:
        print("❌ Error sending email.")

if __name__ == "__main__":
    main()
