#!/usr/bin/env python3
"""
InternGenius Setup Script
Helps users set up the project with proper MongoDB configuration
"""

import os
from getpass import getpass
import secrets
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("🎓" + "="*60 + "🎓")
    print("    INTERNGENIUS - NATIONAL INTERNSHIP PORTAL SETUP")
    print("🎓" + "="*60 + "🎓")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. You have:", sys.version)
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def setup_virtual_environment():
    """Set up virtual environment"""
    print("\n📦 Setting up virtual environment...")
    
    if not os.path.exists('venv'):
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("✅ Virtual environment created successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            return False
    else:
        print("✅ Virtual environment already exists")
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📋 Installing dependencies...")
    
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip.exe')
    else:  # Linux/Mac
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    if not os.path.exists(pip_path):
        print("❌ Virtual environment not properly set up")
        return False
    
    try:
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def setup_environment_file():
    """Set up environment configuration file"""
    print("\n⚙️ Setting up environment configuration...")
    
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    # Read the full connection URI securely; do not embed credentials in source code.
    mongo_uri = os.getenv("MONGO_URI", "").strip()
    if not mongo_uri:
        mongo_uri = getpass("Paste MongoDB connection URI (input hidden; Enter to skip): ").strip()
    if mongo_uri and not mongo_uri.startswith(("mongodb://", "mongodb+srv://")):
        print("❌ MONGO_URI must start with mongodb:// or mongodb+srv://")
        return False
    if not mongo_uri:
        mongo_uri = "mongodb://localhost:27017/interngenius"
        print("💡 Using local MongoDB; the app can fall back to offline demo mode")
    
    # Create .env file
    env_content = f"""# InternGenius Environment Configuration

# Flask Configuration
SECRET_KEY={secrets.token_urlsafe(32)}
FLASK_ENV=development

# MongoDB Configuration
MONGO_URI={mongo_uri}

# Mail Configuration (Optional - for future features)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Security Settings
WTF_CSRF_ENABLED=true
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_setup():
    """Test the setup"""
    print("\n🧪 Testing setup...")
    
    # Test MongoDB connection
    try:
        # Determine the correct python path
        if os.name == 'nt':  # Windows
            python_path = os.path.join('venv', 'Scripts', 'python.exe')
        else:  # Linux/Mac
            python_path = os.path.join('venv', 'bin', 'python')
        
        result = subprocess.run([python_path, 'test_mongodb.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if "successfully connected to MongoDB" in result.stdout:
            print("✅ MongoDB connection test passed")
        else:
            print("⚠️ MongoDB connection test failed (app will run in demo mode)")
            
    except Exception as e:
        print(f"⚠️ Could not run MongoDB test: {e}")
    
    print("✅ Setup test completed")

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("   source venv/bin/activate")
    
    print("2. Run the application:")
    print("   python app.py")
    print("3. Open browser:")
    print("   http://127.0.0.1:5000")
    
    print("\n🎮 Demo accounts:")
    print("   Student: any-email@example.com / demo123")
    print("   Company: company@example.com / demo123")
    print("   Admin: admin@example.com / demo123")
    
    print("\n📚 Documentation:")
    print("   Check README.md for detailed instructions")
    print("   Run 'python test_mongodb.py' to test MongoDB connection")

def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    if not check_python_version():
        return False
    
    # Setup steps
    steps = [
        ("🐍 Virtual Environment", setup_virtual_environment),
        ("📦 Dependencies", install_dependencies),
        ("⚙️ Configuration", setup_environment_file),
        ("🧪 Testing", test_setup)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}")
        print("-" * 30)
        if not step_func():
            print(f"❌ Setup failed at step: {step_name}")
            return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)
