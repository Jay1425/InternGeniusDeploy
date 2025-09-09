"""
Student profile model for storing student-specific information.
"""
class StudentProfile:
    def __init__(self, user_id, personal_info, education, skills, interests, experience, preferences):
        self.user_id = user_id
        self.personal_info = personal_info  # dict: phone, dob, address
        self.education = education          # dict: university, degree, year, cgpa
        self.skills = skills                # list of skills
        self.interests = interests          # list of interests
        self.experience = experience        # list of experience dicts
        self.preferences = preferences      # dict: location, duration, stipend_range

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "personal_info": self.personal_info,
            "education": self.education,
            "skills": self.skills,
            "interests": self.interests,
            "experience": self.experience,
            "preferences": self.preferences
        }
