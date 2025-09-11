#!/usr/bin/env python3
"""
MongoDB Connection Test Script
This script tests the MongoDB connection using the same configuration as the main application.
"""

import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB connection with proper error handling"""
    
    # Get MongoDB URI from environment or use default
    mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://jayraychura13_db_user:YOUR_PASSWORD@interngenius.iwai3zh.mongodb.net/?retryWrites=true&w=majority&appName=InternGenius')
    
    print("🔄 Testing MongoDB Connection...")
    print(f"📋 URI: {mongo_uri[:60]}...")
    
    try:
        # Create MongoDB client with ServerApi
        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        
        # Send a ping to confirm successful connection
        client.admin.command('ping')
        print("✅ Pinged your deployment. You successfully connected to MongoDB!")
        
        # Test database operations
        db = client.interngenius
        
        # Test collections access
        print("📊 Available collections:")
        collections = db.list_collection_names()
        if collections:
            for collection in collections:
                print(f"   - {collection}")
        else:
            print("   - No collections found (this is normal for a new database)")
        
        # Test a simple write/read operation
        test_collection = db.connection_test
        test_doc = {"test": True, "timestamp": "2025-09-11", "message": "MongoDB connection successful!"}
        
        # Insert test document
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read test document
        found_doc = test_collection.find_one({"test": True})
        if found_doc:
            print(f"✅ Test document retrieved: {found_doc['message']}")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        # Close connection
        client.close()
        print("✅ MongoDB connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your .env file has the correct MONGO_URI")
        print("2. Ensure your MongoDB Atlas cluster is running")
        print("3. Verify your IP address is whitelisted in MongoDB Atlas")
        print("4. Check your username and password are correct")
        print("5. Ensure network connectivity to MongoDB Atlas")
        return False

def create_env_file():
    """Create a sample .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        env_content = """# MongoDB Configuration
# Replace YOUR_PASSWORD with your actual MongoDB password
MONGO_URI=mongodb+srv://jayraychura13_db_user:YOUR_PASSWORD@interngenius.iwai3zh.mongodb.net/?retryWrites=true&w=majority&appName=InternGenius

# Flask Configuration
SECRET_KEY=your-secret-key-for-development
FLASK_ENV=development
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("📝 Created .env file template - please update with your MongoDB password")
        return False
    return True

if __name__ == "__main__":
    print("🚀 InternGenius MongoDB Connection Test")
    print("="*50)
    
    # Check if .env file exists
    if not create_env_file():
        print("❗ Please update the .env file with your MongoDB password and run again")
        exit(1)
    
    # Test the connection
    success = test_mongodb_connection()
    
    if success:
        print("\n🎉 Your MongoDB setup is working perfectly!")
        print("📱 You can now run the main application with: python app.py")
    else:
        print("\n⚠️ MongoDB connection failed, but don't worry!")
        print("💾 The application will run in demo mode with all features working")
        print("🔧 Fix the connection when you're ready for production")
