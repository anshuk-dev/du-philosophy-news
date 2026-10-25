"""
Configuration settings for Delhi University (DU) Philosophy Faculty Vacancy Tracker.
"""

import os

# Auto-load local .env if present
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    try:
        with open(_env_path, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and "=" in _line and not _line.startswith("#"):
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip())
    except Exception:
        pass

# Recipient Email for Vacancy Notifications
DEFAULT_RECIPIENT_EMAIL = "anshu.philosophy@gmail.com"
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", DEFAULT_RECIPIENT_EMAIL)

# Gmail SMTP Configuration (Fetched from GitHub Secrets, .env or Environment)
GMAIL_USER = os.environ.get("GMAIL_USER", "anshu.philosophy@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Target Keywords for Philosophy
PHILOSOPHY_KEYWORDS = [
    "philosophy",
    "philosophical",
    "दर्शनशास्त्र",
    "दर्शन शास्त्र",
    "दर्शन",
]

# Vacancy & Faculty Keywords
VACANCY_KEYWORDS = [
    "guest faculty",
    "assistant professor",
    "ad-hoc",
    "adhoc",
    "walk-in",
    "walk in",
    "interview",
    "panel",
    "recruitment",
    "vacancy",
    "vacancies",
    "empanelment",
    "appointment",
]

# List of DU Colleges offering Philosophy
DU_PHILOSOPHY_COLLEGES = [
    "Department of Philosophy, DU",
    "Hindu College",
    "St. Stephen's College",
    "Miranda House",
    "Lady Shri Ram College for Women (LSR)",
    "Ramjas College",
    "Hansraj College",
    "Kirori Mal College (KMC)",
    "Gargi College",
    "Indraprastha College for Women (IPCW)",
    "Kamala Nehru College",
    "Daulat Ram College",
    "Dyal Singh College",
    "Mata Sundri College for Women",
    "Maitreyi College",
    "Shyama Prasad Mukherji College (SPM)",
    "Vivekananda College",
    "Janki Devi Memorial College (JDMC)",
    "Ramanujan College",
    "Lakshmibai College",
    "Shivaji College",
    "Bharati College",
    "Deshbandhu College",
    "Zakir Husain Delhi College",
    "Satyawati College",
    "Delhi College of Arts and Commerce (DCAC)",
]

# Request Headers
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
}

# Request Timeout (seconds)
REQUEST_TIMEOUT = 15

# File Paths
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(DATA_DIR, "notices_history.json")
README_FILE = os.path.join(DATA_DIR, "README.md")
