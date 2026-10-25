"""
Data models for Philosophy Vacancy Notices with deep PDF extraction fields.
"""

import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class VacancyNotice:
    id: str
    title: str
    college: str
    post_type: str
    link: str
    pdf_link: Optional[str] = None
    date_posted: Optional[str] = None
    source: str = "DU Portal"
    discovered_at: str = ""
    # Deep extracted information from official notice/PDF
    vacancies_count: str = "01 Post"
    category: str = "UR / All Eligible"
    interview_date: str = "Check PDF"
    reporting_time: str = "Report 30 mins before"
    venue: str = "Principal Office / Committee Room"
    deadline: str = ""

    def __post_init__(self):
        if not self.discovered_at:
            self.discovered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        if not self.id:
            self.id = self.generate_id(self.title, self.link, self.pdf_link)

    @staticmethod
    def generate_id(title: str, link: str, pdf_link: Optional[str] = None) -> str:
        """Create a deterministic unique identifier hash for deduplication."""
        base = f"{title.strip().lower()}|{(pdf_link or link or '').strip().lower()}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "VacancyNotice":
        # Handle backward compatibility for older JSON entries without new fields
        valid_fields = {
            "id", "title", "college", "post_type", "link", "pdf_link",
            "date_posted", "source", "discovered_at", "vacancies_count",
            "category", "interview_date", "reporting_time", "venue", "deadline"
        }
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)
