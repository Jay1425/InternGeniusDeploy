"""
Company profile model for storing company-specific information.
"""
class CompanyProfile:
    def __init__(self, user_id, company_name, description, website, location, internships_posted):
        self.user_id = user_id
        self.company_name = company_name
        self.description = description
        self.website = website
        self.location = location
        self.internships_posted = internships_posted  # list of internship IDs

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "company_name": self.company_name,
            "description": self.description,
            "website": self.website,
            "location": self.location,
            "internships_posted": self.internships_posted
        }
