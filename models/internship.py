"""
Internship model for storing internship opportunity details.
"""
from datetime import datetime

class Internship:
    def __init__(self, company_id, title, description, requirements, location, mode, sector, duration, stipend, posted_at=None):
        self.company_id = company_id
        self.title = title
        self.description = description
        self.requirements = requirements  # list of required skills
        self.location = location
        self.mode = mode                  # 'remote' or 'in-person'
        self.sector = sector
        self.duration = duration
        self.stipend = stipend
        self.posted_at = posted_at or datetime.utcnow()

    def to_dict(self):
        return {
            "company_id": self.company_id,
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "location": self.location,
            "mode": self.mode,
            "sector": self.sector,
            "duration": self.duration,
            "stipend": self.stipend,
            "posted_at": self.posted_at
        }
