import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from flask import session

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()

    def test_index_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'InternGenius', response.data)

    def test_student_registration_page(self):
        response = self.app.get('/direct_student_registration', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student Registration', response.data)
    
    def test_student_registration_submission(self):
        with self.app as client:
            # Basic test data for student registration
            data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'testuser@example.com',
                'phone': '1234567890',
                'dob': '2000-01-01',
                'gender': 'male',
                'category': 'general',
                'aadhaar': '123456789012',
                'nationality': 'Indian',
                'address_line1': 'Test Address',
                'city': 'Test City',
                'state': 'gujarat',
                'pincode': '123456',
                'qualification_1': 'bachelors',
                'specialization_1': 'Computer Science',
                'institution_1': 'Test University',
                'passing_year_1': '2022',
                'percentage_1': '85',
                'skills': 'Python, Java',
                'soft_skills': 'Communication, Leadership',
                'languages': 'English, Hindi',
                'preferred_locations': 'Mumbai, Pune',
                'internship_duration': '3-6_months',
                'work_mode': 'remote',
                'availability': 'immediately',
                'terms_accepted': 'on',
                'data_accuracy': 'on',
                'verification_consent': 'on'
            }
            
            response = client.post('/register_student', data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Registration Successful', response.data)
            self.assertTrue('registration_data' in session)
    
    def test_invalid_routes(self):
        response = self.app.get('/nonexistent_route', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)

if __name__ == '__main__':
    unittest.main()
