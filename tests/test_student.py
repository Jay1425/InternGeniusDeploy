import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from flask import session

class StudentTestCase(unittest.TestCase):
    """Test cases for student registration and profile functionality"""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()

    def test_student_registration_form_loads(self):
        """Test that student registration form loads"""
        response = self.app.get('/direct_student_registration')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student Registration', response.data)

    def test_student_profile_redirect_without_session(self):
        """Test that profile redirects when no registration data in session"""
        response = self.app.get('/student_profile', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Should redirect to registration page

    def test_valid_student_registration(self):
        """Test successful student registration"""
        with self.app as client:
            data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '9876543210',
                'dob': '2000-05-15',
                'gender': 'male',
                'category': 'general',
                'aadhaar': '123456789012',
                'nationality': 'Indian',
                'address_line1': '123 Test Street',
                'city': 'Mumbai',
                'state': 'maharashtra',
                'pincode': '400001',
                'qualification_1': 'bachelors',
                'specialization_1': 'Computer Science',
                'institution_1': 'Mumbai University',
                'passing_year_1': '2023',
                'percentage_1': '85%',
                'skills': 'Python, JavaScript, React',
                'soft_skills': 'Communication, Teamwork',
                'languages': 'English, Hindi, Marathi',
                'interests': 'software_development,web_development',
                'preferred_locations': 'Mumbai, Pune, Remote',
                'internship_duration': '3-6_months',
                'work_mode': 'hybrid',
                'availability': 'within_1_month',
                'terms_accepted': 'on',
                'data_accuracy': 'on',
                'verification_consent': 'on'
            }
            
            response = client.post('/register_student', data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
