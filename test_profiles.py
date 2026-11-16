#!/usr/bin/env python3
"""
Test script to verify MongoDB profile data storage
"""

import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables
load_dotenv()

def test_user_profiles():
    """Test and display user profiles from MongoDB"""
    
    # Get MongoDB URI from environment
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        raise RuntimeError('MONGO_URI must be configured before running this test')
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        db = client.interngenius
        
        print("🔍 Checking user profiles in MongoDB...")
        print("="*60)
        
        # Get all users
        users = list(db.users.find())
        
        if not users:
            print("❌ No users found in database")
            return
        
        print(f"✅ Found {len(users)} user(s) in database\n")
        
        for i, user in enumerate(users, 1):
            print(f"👤 User {i}: {user.get('first_name', 'Unknown')} {user.get('last_name', '')}")
            print(f"   📧 Email: {user.get('email', 'N/A')}")
            print(f"   🎭 Role: {user.get('role', 'N/A')}")
            print(f"   ✅ Profile Completed: {user.get('profile_completed', False)}")
            
            # Check for detailed profile data
            profile_data = user.get('profile_data', {})
            if profile_data:
                print(f"   📊 Profile Data Available:")
                print(f"      📱 Phone: {profile_data.get('phone', 'N/A')}")
                print(f"      📅 DOB: {profile_data.get('date_of_birth', 'N/A')}")
                print(f"      🏠 City: {profile_data.get('city', 'N/A')}")
                print(f"      🎓 University: {profile_data.get('university', 'N/A')}")
                print(f"      💼 Skills: {profile_data.get('technical_skills', 'N/A')}")
                print(f"      🎯 Interests: {profile_data.get('interests', 'N/A')}")
            
            # Check for structured profile fields
            if user.get('phone'):
                print(f"   📊 Structured Profile Data Available:")
                print(f"      📱 Phone: {user.get('phone', 'N/A')}")
                print(f"      🏠 Address: {user.get('address', {}).get('city', 'N/A')}")
                print(f"      🎓 Education: {user.get('education', {}).get('university', 'N/A')}")
                
            print(f"   🆔 MongoDB ID: {user.get('_id')}")
            print("-" * 50)
        
        # Show detailed view of one user
        if users:
            print("\n📋 Detailed view of first user:")
            pprint(users[0])
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")

def test_specific_user(email):
    """Test specific user profile by email"""
    
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        raise RuntimeError('MONGO_URI must be configured before running this test')
    
    try:
        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        db = client.interngenius
        
        user = db.users.find_one({'email': email})
        
        if user:
            print(f"✅ Found user: {email}")
            pprint(user)
        else:
            print(f"❌ User not found: {email}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎓 InternGenius Profile Data Test")
    print("="*40)
    
    # Test all profiles
    test_user_profiles()
    
    # Test specific user if provided
    test_email = input("\n🔍 Enter email to check specific user (or press Enter to skip): ").strip()
    if test_email:
        print(f"\n🔍 Checking user: {test_email}")
        test_specific_user(test_email)
