#!/usr/bin/env python3
"""
Simple MongoDB test for comprehensive registration
"""

import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Load environment variables
load_dotenv()

def main():
    """Test MongoDB connection and user data"""
    print("🧪 Testing Comprehensive Student Registration Data")
    print("=" * 50)
    
    try:
        # Connect to MongoDB Atlas
        uri = os.getenv('MONGO_URI')
        if not uri:
            raise RuntimeError('MONGO_URI must be configured')
        print(f"🔗 Connecting to: {uri[:50]}...")
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        db = client.get_database("interngeniusdb")
        
        # Check current user
        user = db.users.find_one({'email': 'jayraychura3@gmail.com'})
        if user:
            print(f"\n👤 Found user: {user.get('first_name')} {user.get('last_name')}")
            print(f"📧 Email: {user.get('email')}")
            print(f"📱 Phone: {user.get('phone', 'NOT PROVIDED')}")
            print(f"🎂 DOB: {user.get('date_of_birth', 'NOT PROVIDED')}")
            print(f"👤 Gender: {user.get('gender', 'NOT PROVIDED')}")
            print(f"🏷️ Category: {user.get('category', 'NOT PROVIDED')}")
            print(f"🆔 Aadhaar: {user.get('aadhaar_number', 'NOT PROVIDED')}")
            print(f"🌍 Nationality: {user.get('nationality', 'NOT PROVIDED')}")
            print(f"🎓 Education: {user.get('current_education', 'NOT PROVIDED')}")
            print(f"🏫 Institution: {user.get('institution_name', 'NOT PROVIDED')}")
            print(f"✅ Profile Complete: {user.get('profile_completed', False)}")
            
            # Delete existing user for fresh test
            db.users.delete_one({'email': 'jayraychura3@gmail.com'})
            print(f"\n🧹 Deleted existing user for fresh test")
        else:
            print("❌ No existing user found")
        
        print("\n✨ Ready for comprehensive registration test!")
        print("📋 Steps:")
        print("1. Go to: http://127.0.0.1:5000/direct_student_registration")
        print("2. Fill complete form with all details")
        print("3. Run: python simple_test_mongo.py")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
