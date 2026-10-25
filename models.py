"""
Data models for Philosophy Vacancy Notices.
"""

import hashlib
import json
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
        return cls(**data)
