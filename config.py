import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'interngenius-secret-key-change-in-production'
    
    # MongoDB Configuration with improved connection string
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb+srv://jayraychura13_db_user:jUhWmtYndMBViwq5@interngenius.iwai3zh.mongodb.net/?retryWrites=true&w=majority&appName=InternGenius'
    
    # Flask-Login Configuration
    REMEMBER_COOKIE_DURATION = 86400  # 1 day in seconds
    
    # Security
    WTF_CSRF_ENABLED = True
    
    # Mail Configuration (for future use)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # ML Models Configuration
    ML_MODELS_PATH = 'ml_module/models/'
    ML_DATA_PATH = 'ml_module/data/'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    MONGO_URI = os.environ.get('DEV_MONGO_URI') or 'mongodb+srv://jayraychura13_db_user:jUhWmtYndMBViwq5@interngenius.iwai3zh.mongodb.net/interngenius_dev'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    MONGO_URI = os.environ.get('PROD_MONGO_URI') or 'mongodb+srv://jayraychura13_db_user:jUhWmtYndMBViwq5@interngenius.iwai3zh.mongodb.net/interngenius_prod'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGO_URI = 'mongodb+srv://jayraychura13_db_user:jUhWmtYndMBViwq5@interngenius.iwai3zh.mongodb.net/interngenius_test'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
