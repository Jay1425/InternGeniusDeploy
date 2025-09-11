#!/usr/bin/env python3
"""
Test script for comprehensive student registration
"""

import os
import sys
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId

# Load environment variables
load_dotenv()

# Prevent Flask app from starting when importing
os.environ['FLASK_ENV'] = 'testing'

def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        uri = os.getenv('MONGODB_URI')
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return None

def clean_test_users(db):
    """Clean up test users"""
    try:
        # Remove test users
        result = db.users.delete_many({
            'email': {'$in': ['jayraychura3@gmail.com', 'test@example.com']}
        })
        print(f"🧹 Cleaned up {result.deleted_count} test users")
        return True
    except Exception as e:
        print(f"❌ Error cleaning users: {e}")
        return False

def check_user_data(db, email):
    """Check comprehensive user data storage"""
    try:
        user = db.users.find_one({'email': email})
        if user:
            print(f"\n👤 User found: {user.get('first_name')} {user.get('last_name')}")
            print(f"📧 Email: {user.get('email')}")
            print(f"📱 Phone: {user.get('phone', 'Not provided')}")
            print(f"🎂 DOB: {user.get('date_of_birth', 'Not provided')}")
            print(f"👤 Gender: {user.get('gender', 'Not provided')}")
            print(f"🏷️ Category: {user.get('category', 'Not provided')}")
            print(f"🆔 Aadhaar: {user.get('aadhaar_number', 'Not provided')}")
            print(f"🌍 Nationality: {user.get('nationality', 'Not provided')}")
            print(f"🎓 Education: {user.get('current_education', 'Not provided')}")
            print(f"🏫 Institution: {user.get('institution_name', 'Not provided')}")
            print(f"📚 Field of Study: {user.get('field_of_study', 'Not provided')}")
            print(f"📊 CGPA: {user.get('cgpa', 'Not provided')}")
            print(f"🛠️ Skills: {user.get('skills', [])}")
            print(f"📍 Preferred Locations: {user.get('preferred_locations', [])}")
            print(f"✅ Profile Complete: {user.get('profile_completed', False)}")
            
            # Count total fields with data
            total_fields = 0
            filled_fields = 0
            
            important_fields = [
                'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 
                'gender', 'category', 'aadhaar_number', 'nationality', 
                'current_education', 'institution_name', 'field_of_study'
            ]
            
            for field in important_fields:
                total_fields += 1
                if user.get(field):
                    filled_fields += 1
            
            completion_rate = (filled_fields / total_fields) * 100
            print(f"\n📊 Profile Completion: {filled_fields}/{total_fields} ({completion_rate:.1f}%)")
            
            return user
        else:
            print(f"❌ No user found with email: {email}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking user data: {e}")
        return None

def main():
    """Main test function"""
    print("🧪 Testing Comprehensive Student Registration")
    print("=" * 50)
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    if not client:
        return
    
    db = client.get_database("interngeniusdb")
    
    # Check existing user
    print("\n1. Checking existing user data:")
    existing_user = check_user_data(db, 'jayraychura3@gmail.com')
    
    # Clean up for fresh test
    print("\n2. Cleaning up test data:")
    clean_test_users(db)
    
    print("\n✨ Ready for fresh registration test!")
    print("📋 Next steps:")
    print("1. Go to http://127.0.0.1:5000/direct_student_registration")
    print("2. Fill out the complete registration form")
    print("3. Run this script again to verify comprehensive data storage")
    
    client.close()

if __name__ == "__main__":
    main()
