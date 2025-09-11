#!/usr/bin/env python3
"""
Test script for enhanced User model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user_model import User
from datetime import datetime

def test_enhanced_user_model():
    """Test the enhanced User model functionality"""
    print("🧪 Testing Enhanced User Model")
    print("=" * 40)
    
    # Test comprehensive student creation
    print("\n1. Testing comprehensive student creation:")
    
    form_data = {
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'first_name': 'Test',
        'middle_name': 'Kumar',
        'last_name': 'Student',
        'phone': '9876543210',
        'date_of_birth': datetime(2000, 1, 15),
        'gender': 'Male',
        'category': 'General',
        'aadhaar_number': '123456789012',
        'nationality': 'Indian',
        'current_education': 'B.Tech',
        'institution_name': 'Test University',
        'field_of_study': 'Computer Science',
        'year_of_study': '3rd Year',
        'cgpa': 8.5,
        'skills': ['Python', 'Java', 'Web Development'],
        'preferred_locations': ['Mumbai', 'Bangalore'],
        'internship_duration': '6 months'
    }
    
    # Create comprehensive student
    user = User.create_comprehensive_student(form_data)
    
    # Test full name with middle name
    print(f"✅ Full Name: {user.get_full_name()}")
    print(f"✅ Display Name: {user.get_display_name()}")
    print(f"✅ Profile Completion: {user.get_profile_completion_percentage():.1f}%")
    print(f"✅ Complete Profile: {user.has_complete_profile()}")
    
    # Test to_dict conversion
    user_dict = user.to_dict()
    print(f"✅ Dictionary Keys: {len(user_dict.keys())} fields")
    
    # Test password check
    print(f"✅ Password Check: {user.check_password('TestPass123!')}")
    print(f"✅ Wrong Password: {user.check_password('WrongPass')}")
    
    print("\n2. Testing field access:")
    print(f"📧 Email: {user.email}")
    print(f"📱 Phone: {user.phone}")
    print(f"🎂 DOB: {user.date_of_birth}")
    print(f"🎓 Education: {user.current_education}")
    print(f"🏫 Institution: {user.institution_name}")
    print(f"🛠️ Skills: {user.skills}")
    print(f"📍 Locations: {user.preferred_locations}")
    print(f"✅ Profile Status: {user.profile_completed}")
    
    print("\n✅ Enhanced User Model Test Complete!")
    return True

if __name__ == "__main__":
    try:
        test_enhanced_user_model()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
