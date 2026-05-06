from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class JobLead:
    company: str
    role: str
    category: str
    location: str
    link: str
    source: str
    snippet: str = ""
    match_score: int = 0
    missing_skills: list[str] = field(default_factory=list)
    found_date: str = field(default_factory=lambda: date.today().isoformat())

    def airtable_fields(self, resume_used: str | None = None) -> dict[str, object]:
        return {
            "Company": self.company,
            "Role": self.role,
            "Category": self.category,
            "Location": self.location,
            "Link": self.link,
            "Status": "Pending",
            "Match Score": self.match_score,
            "Resume Used": resume_used or "",
            "Applied": False,
            "Date": self.found_date,
            "Notes": self.snippet[:500],
        }
