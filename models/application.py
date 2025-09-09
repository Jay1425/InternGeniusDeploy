"""
Application model for storing internship applications.
"""
from datetime import datetime

class Application:
    def __init__(self, student_id, internship_id, status, applied_at=None, feedback=None):
        self.student_id = student_id
        self.internship_id = internship_id
        self.status = status              # e.g., 'applied', 'shortlisted', 'rejected', 'accepted'
        self.applied_at = applied_at or datetime.utcnow()
        self.feedback = feedback

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "internship_id": self.internship_id,
            "status": self.status,
            "applied_at": self.applied_at,
            "feedback": self.feedback
        }
