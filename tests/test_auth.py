import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

class AuthTestCase(unittest.TestCase):
    """Test cases for authentication routes"""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()

    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'InternGenius', response.data)

    def test_signup_page_loads(self):
        """Test that signup page loads successfully"""
        response = self.app.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'InternGenius', response.data)

if __name__ == '__main__':
    unittest.main()
