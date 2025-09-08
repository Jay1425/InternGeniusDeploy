#!/usr/bin/env python3
"""
InternGenius Setup Script
Automated setup for the InternGenius Flask application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(message):
    """Print setup step with formatting"""
    print(f"\n🔧 {message}")
    print("-" * 50)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_python_version():
    """Check if Python version is 3.8+"""
    print_step("Checking Python version")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.8+ required. Current version: {version.major}.{version.minor}.{version.micro}")
        return False

def create_virtual_environment():
    """Create Python virtual environment"""
    print_step("Creating virtual environment")
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_success("Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to create virtual environment")
        return False

def get_venv_python():
    """Get the path to Python executable in virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "python.exe")
    else:  # Unix/Linux/MacOS
        return os.path.join("venv", "bin", "python")

def install_requirements():
    """Install Python requirements"""
    print_step("Installing Python packages")
    
    python_exe = get_venv_python()
    
    try:
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_success("All packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install requirements")
        return False

def setup_environment_file():
    """Setup .env file from template"""
    print_step("Setting up environment configuration")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print_info(".env file already exists, skipping...")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print_success("Environment file created from template")
        print_info("⚠️  Please edit .env file with your configuration:")
        print_info("   - MongoDB connection string")
        print_info("   - Secret keys")
        print_info("   - Email settings (optional)")
        return True
    else:
        print_error(".env.example template not found")
        return False

def create_directories():
    """Create necessary directories"""
    print_step("Creating application directories")
    
    directories = [
        "logs",
        "static/uploads",
        "ml_module/models",
        "data/temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print_success("All directories created")
    return True

def check_mongodb():
    """Check if MongoDB is accessible"""
    print_step("Checking MongoDB connection")
    
    try:
        import pymongo
        # Try to connect to default MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()  # Force connection
        print_success("MongoDB connection successful")
        client.close()
        return True
    except:
        print_info("MongoDB not accessible locally")
        print_info("Options:")
        print_info("1. Install MongoDB locally")
        print_info("2. Use MongoDB Atlas (cloud)")
        print_info("3. Update MONGO_URI in .env file")
        return False

def generate_secret_key():
    """Generate a secure secret key"""
    import secrets
    return secrets.token_urlsafe(32)

def update_env_secrets():
    """Update .env file with generated secrets"""
    print_step("Generating secure secret keys")
    
    env_file = Path(".env")
    if not env_file.exists():
        print_error(".env file not found")
        return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Generate new secret key
    new_secret = generate_secret_key()
    
    # Replace the template secret key
    updated_content = content.replace(
        "interngenius-super-secret-key-change-in-production",
        new_secret
    )
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print_success("Secret keys generated and updated")
    return True

def run_application():
    """Run the Flask application"""
    print_step("Starting Flask application")
    
    python_exe = get_venv_python()
    
    print_info("Starting InternGenius application...")
    print_info("Access the application at: http://127.0.0.1:5000")
    print_info("Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([python_exe, "run.py"], check=True)
    except KeyboardInterrupt:
        print_info("\nApplication stopped by user")
    except subprocess.CalledProcessError:
        print_error("Failed to start application")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 InternGenius Setup Script")
    print("=" * 50)
    print("This script will set up your InternGenius development environment")
    print()
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print_error("app.py not found. Please run this script from the InternGenius root directory")
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing requirements", install_requirements),
        ("Setting up environment file", setup_environment_file),
        ("Updating secret keys", update_env_secrets),
        ("Creating directories", create_directories),
        ("Checking MongoDB", check_mongodb)
    ]
    
    # Run setup steps
    for step_name, step_func in steps:
        if not step_func():
            print_error(f"Setup failed at: {step_name}")
            print_info("Please resolve the issue and run the script again")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print_success("🎉 Setup completed successfully!")
    print_info("Next steps:")
    print_info("1. Edit .env file with your configuration")
    print_info("2. Ensure MongoDB is running")
    print_info("3. Run 'python run.py' to start the application")
    print()
    
    # Ask if user wants to start the application
    try:
        start_app = input("Would you like to start the application now? (y/n): ").lower().strip()
        if start_app in ['y', 'yes']:
            run_application()
    except KeyboardInterrupt:
        print_info("\nSetup complete. Run 'python run.py' when ready to start the application.")

if __name__ == "__main__":
    main()
