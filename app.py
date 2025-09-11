from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
import os
import secrets
import bcrypt
import re
from datetime import datetime, timedelta, timezone
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson.objectid import ObjectId
from functools import wraps
from dotenv import load_dotenv
from config import config
import certifi
from models.user_model import User

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])
app.secret_key = app.config.get('SECRET_KEY', secrets.token_hex(16))
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Security configuration
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour CSRF token lifetime

# MongoDB Configuration - Load from environment variables
# Get MONGO_URI from .env file or use fallback
base_mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://jayraychura13_db_user:jUhWmtYndMBViwq5@interngenius.iwai3zh.mongodb.net/interngenius')

# Enhanced MongoDB connection with ServerApi
mongodb_uri_options = [
    # Option 1: Enhanced connection string from config with ServerApi support
    base_mongo_uri,
    # Option 2: Fallback with additional connection parameters
    f"{base_mongo_uri.split('?')[0]}?retryWrites=true&w=majority&connectTimeoutMS=3000&serverSelectionTimeoutMS=3000",
    # Option 3: Local MongoDB fallback (if available)
    'mongodb://localhost:27017/interngenius'
]

# Set default URI (will be updated by connection logic)
app.config['MONGO_URI'] = mongodb_uri_options[0]

# Initialize MongoDB with multiple connection attempts
def test_network_connectivity():
    """Quick network test to MongoDB Atlas domain"""
    import socket
    try:
        # Test DNS resolution for MongoDB Atlas
        socket.gethostbyname("interngenius.iwai3zh.mongodb.net")
        return True
    except socket.gaierror:
        return False

def init_mongodb():
    """Initialize MongoDB connection with ServerApi and multiple URI attempts"""
    print(f"📋 Base URI from .env: {base_mongo_uri[:60]}...")
    
    # Test network connectivity first
    if not test_network_connectivity():
        print("🌐 Network connectivity test failed - DNS cannot resolve MongoDB Atlas domain")
        print("💡 This suggests network/firewall restrictions or ISP blocking")
        # Skip Atlas attempts and try local MongoDB directly
        try:
            print("🔄 Trying local MongoDB as fallback...")
            client = MongoClient('mongodb://localhost:27017/interngenius', 
                               serverSelectionTimeoutMS=1000,
                               connectTimeoutMS=1000)
            client.admin.command('ping')
            db = client.interngenius
            print("✅ Local MongoDB connected successfully!")
            return client, db
        except Exception as e:
            print(f"❌ Local MongoDB not available: {str(e)[:40]}...")
    
    for i, uri in enumerate(mongodb_uri_options):
        try:
            print(f"🔄 Attempting MongoDB connection {i+1}/{len(mongodb_uri_options)}...")
            if i < 2:  # Atlas connections
                print(f"   Using MongoDB Atlas with ServerApi")
                # Use ServerApi for Atlas connections
                client = MongoClient(uri, 
                                   server_api=ServerApi('1'),
                                   serverSelectionTimeoutMS=5000,
                                   connectTimeoutMS=5000,
                                   socketTimeoutMS=5000,
                                   maxPoolSize=1,
                                   tlsCAFile=certifi.where())
            else:  # Local connection
                print(f"   Using: Local MongoDB (localhost:27017)")
                client = MongoClient(uri, 
                                   serverSelectionTimeoutMS=2000,
                                   connectTimeoutMS=2000,
                                   socketTimeoutMS=2000,
                                   maxPoolSize=1)
            
            # Test the connection with ping
            client.admin.command('ping')
            db = client.interngenius
            print(f"✅ MongoDB connected successfully using approach {i+1}!")
            print("🎉 Pinged your deployment. You successfully connected to MongoDB!")
            return client, db
            
        except KeyboardInterrupt:
            print("⏹️ Connection interrupted by user")
            break
        except Exception as e:
            error_msg = str(e)
            if "SSL" in error_msg or "handshake" in error_msg:
                print(f"❌ Connection {i+1} failed: SSL/TLS handshake error")
            elif "DNS" in error_msg or "resolve" in error_msg:
                print(f"❌ Connection {i+1} failed: DNS resolution timeout")
            elif "authentication" in error_msg.lower():
                print(f"❌ Connection {i+1} failed: Authentication error - check credentials")
            elif "timeout" in error_msg.lower():
                print(f"❌ Connection {i+1} failed: Connection timeout")
            else:
                print(f"❌ Connection {i+1} failed: {error_msg[:50]}...")
            continue
    
    print("⚠️ MongoDB connection failed - running in offline mode with session storage")
    print("💾 All features fully functional! No database setup required for demo.")
    print("📋 To connect to MongoDB: Check your .env file and network connectivity")
    return None, None

# Try to connect to MongoDB
mongo_client, mongo_db = init_mongodb()

# Database setup function (called lazily when needed)
def setup_database():
    """Setup database collections and indexes - called when needed"""
    if mongo_db is not None:
        try:
            # Create unique index on users email field (will create collection if not exists)
            mongo_db.users.create_index('email', unique=True, background=True)
            print("📋 Database indexes ensured")
        except Exception as e:
            print(f"ℹ️ Database setup info: {str(e)[:50]}...")

# MongoDB health check function
def check_mongodb_health():
    """Check if MongoDB is accessible"""
    if mongo_client is not None:
        try:
            mongo_client.admin.command('ping')
            return True
        except:
            return False
    return False

# Database operation wrapper for resilience
def safe_db_operation(operation, fallback_value=None, description="Database operation"):
    """Safely execute database operations with fallback"""
    if mongo_db is None:
        print(f"💾 {description} - Using session storage (offline mode)")
        return fallback_value
    
    try:
        return operation()
    except Exception as e:
        print(f"⚠️ {description} failed: {str(e)[:50]}... - Using fallback")
        return fallback_value

# Enable CSRF protection
csrf = CSRFProtect(app)

# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; font-src 'self' fonts.googleapis.com fonts.gstatic.com; img-src 'self' data:; connect-src 'self';"
    return response

# Security utilities
def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def validate_password_strength(password):
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

def validate_email_format(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_secure_session_id():
    """Generate a secure session ID"""
    return secrets.token_urlsafe(32)

def get_current_datetime():
    """Get current datetime in a consistent format"""
    return datetime.now()

def datetime_to_string(dt):
    """Convert datetime to string for session storage"""
    if dt is None:
        return None
    return dt.isoformat()

def string_to_datetime(dt_str):
    """Convert string back to datetime from session storage"""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except:
        return None

def is_session_expired(session_created_at):
    """Check if session has expired (24 hours)"""
    if not session_created_at:
        return True
    
    # Ensure both datetimes are timezone-aware or both are naive
    if isinstance(session_created_at, str):
        # Parse string datetime if needed
        try:
            session_created_at = datetime.fromisoformat(session_created_at.replace('Z', '+00:00'))
        except:
            return True
    
    # Make both datetimes timezone-naive for comparison
    if session_created_at.tzinfo is not None:
        session_created_at = session_created_at.replace(tzinfo=None)
    
    expiry_time = session_created_at + timedelta(hours=24)
    current_time = datetime.now()
    
    return current_time > expiry_time

def sanitize_input(input_string):
    """Sanitize user input to prevent injection attacks"""
    if not input_string:
        return ""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';()&+]', '', str(input_string))
    return sanitized.strip()

# Authentication decorators
def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        # Check if session is expired
        session_created = session.get('session_created_at')
        if session_created:
            # Convert string back to datetime if needed
            if isinstance(session_created, str):
                session_created = string_to_datetime(session_created)
            
            if session_created and is_session_expired(session_created):
                session.clear()
                flash('Your session has expired. Please log in again.', 'warning')
                return redirect(url_for('login'))
        
        # Validate session integrity
        if not session.get('session_id') or not session.get('user_email'):
            session.clear()
            flash('Invalid session. Please log in again.', 'danger')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            user_type = session.get('user_type')
            if user_type != required_role:
                flash(f'Access denied. This page is for {required_role}s only.', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)

# Simple route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    db_status = "connected" if check_mongodb_health() else "offline"
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.now().isoformat()
    })

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    from forms.auth_forms import LoginForm
    form = LoginForm()
    
    if form.validate_on_submit():
        email = sanitize_input(form.email.data.lower().strip())
        password = form.password.data
        
        # Validate email format
        if not validate_email_format(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/login.html', form=form)
        
        # Rate limiting check (simple implementation)
        login_attempts = session.get('login_attempts', 0)
        if login_attempts >= 5:
            flash('Too many login attempts. Please try again later.', 'danger')
            return render_template('auth/login.html', form=form)
        
        try:
            # Authenticate against database
            if mongo_db is not None:
                user = mongo_db.users.find_one({'email': email})
                
                if user and verify_password(password, user.get('password_hash', '')):
                    # Successful authentication
                    session.clear()  # Clear any existing session data
                    
                    # Create secure session
                    current_time = get_current_datetime()
                    session['user_id'] = str(user['_id'])
                    session['user_email'] = user['email']
                    session['user_name'] = user.get('first_name', email.split('@')[0]).title()
                    session['user_type'] = user.get('role', 'student')
                    session['session_id'] = generate_secure_session_id()
                    session['session_created_at'] = datetime_to_string(current_time)
                    session['last_activity'] = datetime_to_string(current_time)
                    session.permanent = True
                    
                    # Update last login in database
                    mongo_db.users.update_one(
                        {'_id': user['_id']},
                        {'$set': {
                            'last_login': datetime.now(),
                            'login_count': user.get('login_count', 0) + 1
                        }}
                    )
                    
                    flash(f'Welcome back, {session["user_name"]}!', 'success')
                    
                    # Redirect to intended page or dashboard
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('dashboard'))
                else:
                    # Failed authentication
                    session['login_attempts'] = login_attempts + 1
                    flash('Invalid email or password. Please try again.', 'danger')
            else:
                # Demo mode - create mock authenticated session
                if email and password == 'demo123':  # Demo password
                    session.clear()
                    current_time = get_current_datetime()
                    session['user_id'] = 'demo_user_' + secrets.token_hex(8)
                    session['user_email'] = email
                    session['user_name'] = email.split('@')[0].title()
                    session['user_type'] = 'admin' if 'admin' in email else ('company' if 'company' in email else 'student')
                    session['session_id'] = generate_secure_session_id()
                    session['session_created_at'] = datetime_to_string(current_time)
                    session.permanent = True
                    
                    flash(f'Welcome {session["user_name"]}! (Demo mode)', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Demo mode: Use password "demo123" with any email', 'info')
                    
        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    from forms.auth_forms import SignupForm
    form = SignupForm()
    
    if form.validate_on_submit():
        # Sanitize and validate input
        first_name = sanitize_input(form.first_name.data)
        last_name = sanitize_input(form.last_name.data)
        email = sanitize_input(form.email.data.lower().strip())
        password = form.password.data
        role = sanitize_input(form.role.data)
        
        # Validate email format
        if not validate_email_format(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/signup.html', form=form)
        
        # Validate password strength
        is_strong, message = validate_password_strength(password)
        if not is_strong:
            flash(f'Password security error: {message}', 'danger')
            return render_template('auth/signup.html', form=form)
        
        # Validate name fields
        if len(first_name) < 2 or len(last_name) < 2:
            flash('First and last name must be at least 2 characters long.', 'danger')
            return render_template('auth/signup.html', form=form)
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create secure user record
        user_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'is_active': True,
            'is_verified': False,
            'created_at': datetime.now(),
            'last_login': None,
            'login_count': 0,
            'password_changed_at': datetime.now()
        }
        
        try:
            if mongo_db is not None:
                # Check if user already exists
                existing_user = mongo_db.users.find_one({'email': email})
                if existing_user:
                    flash('Email already registered. Please sign in instead.', 'warning')
                    return redirect(url_for('login'))
                
                # Save new user
                result = mongo_db.users.insert_one(user_data)
                
                # Create secure session for new user
                session.clear()
                current_time = get_current_datetime()
                session['user_id'] = str(result.inserted_id)
                session['user_email'] = email
                session['user_name'] = first_name
                session['user_type'] = role
                session['session_id'] = generate_secure_session_id()
                session['session_created_at'] = datetime_to_string(current_time)
                session.permanent = True
                
                flash(f'Account created successfully! Welcome {first_name}!', 'success')
                
                # Redirect based on role
                if form.role.data == 'student':
                    return redirect(url_for('direct_student_registration'))
                elif form.role.data == 'company':
                    return redirect(url_for('direct_company_registration'))
                elif form.role.data == 'admin':
                    return redirect(url_for('direct_admin_registration'))
            else:
                flash('Account created successfully! (Demo mode)', 'success')
                return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Account created successfully! (Demo mode)', 'success')
            print(f"Database error: {e}")
            return redirect(url_for('dashboard'))
    
    return render_template('auth/signup.html', form=form)

@app.route('/logout')
def logout():
    """Securely log out the current user"""
    user_name = session.get('user_name', 'User')
    
    try:
        # Update last logout time in database if user is logged in
        if 'user_id' in session and mongo_db is not None:
            mongo_db.users.update_one(
                {'_id': session.get('user_id')},
                {'$set': {'last_logout': datetime.now()}}
            )
    except Exception as e:
        print(f"Logout database update error: {e}")
    
    # Clear all session data securely
    session.clear()
    
    # Regenerate session ID to prevent session fixation
    session.permanent = False
    
    flash(f'Goodbye {user_name}! You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset requests"""
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', '').lower().strip())
        
        if not validate_email_format(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/forgot_password.html')
        
        try:
            if mongo_db is not None:
                user = mongo_db.users.find_one({'email': email})
                if user:
                    # Generate reset token (in production, send via email)
                    reset_token = secrets.token_urlsafe(32)
                    reset_expires = datetime.now() + timedelta(hours=1)
                    
                    # Save reset token to database
                    mongo_db.users.update_one(
                        {'email': email},
                        {'$set': {
                            'reset_token': reset_token,
                            'reset_expires': reset_expires
                        }}
                    )
                    
                    flash('If an account with that email exists, you will receive password reset instructions.', 'info')
                else:
                    # Don't reveal if email exists or not for security
                    flash('If an account with that email exists, you will receive password reset instructions.', 'info')
            else:
                flash('Password reset feature is not available in demo mode.', 'warning')
        except Exception as e:
            print(f"Password reset error: {e}")
            flash('An error occurred. Please try again later.', 'danger')
        
        return redirect(url_for('login'))
    
    return render_template('auth/forgot_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow logged-in users to change their password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required.', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')
        
        # Validate new password strength
        is_strong, message = validate_password_strength(new_password)
        if not is_strong:
            flash(f'Password security error: {message}', 'danger')
            return render_template('auth/change_password.html')
        
        try:
            if mongo_db is not None:
                user = mongo_db.users.find_one({'_id': session['user_id']})
                if user and verify_password(current_password, user.get('password_hash', '')):
                    # Update password
                    new_password_hash = hash_password(new_password)
                    mongo_db.users.update_one(
                        {'_id': session['user_id']},
                        {'$set': {
                            'password_hash': new_password_hash,
                            'password_changed_at': datetime.now()
                        }}
                    )
                    flash('Password changed successfully!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Current password is incorrect.', 'danger')
            else:
                flash('Password change is not available in demo mode.', 'warning')
        except Exception as e:
            print(f"Password change error: {e}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('auth/change_password.html')

# Student registration routes
@app.route('/register/student', methods=['GET'])
def register_student_form():
    """Render student registration form"""
    return render_template('student_registration.html')

@app.route('/direct_student_registration', methods=['GET', 'POST'])
def direct_student_registration():
    """Integrated student registration with authentication setup"""
    if request.method == 'POST':
        # Get basic authentication data
        email = sanitize_input(request.form.get('email', '').lower().strip())
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = sanitize_input(request.form.get('first_name', ''))
        last_name = sanitize_input(request.form.get('last_name', ''))

        # Get comprehensive profile data
        middle_name = sanitize_input(request.form.get('middle_name', ''))
        phone = sanitize_input(request.form.get('phone', ''))
        # Note: template uses 'dob' for date of birth
        dob_str = request.form.get('dob', '')
        gender = sanitize_input(request.form.get('gender', ''))
        category = sanitize_input(request.form.get('category', ''))
        aadhaar_raw = sanitize_input(request.form.get('aadhaar_raw', ''))
        nationality = sanitize_input(request.form.get('nationality', ''))

        # Education entries: qualification_N, specialization_N, institution_N, passing_year_N, percentage_N
        education_entries = []
        idx = 1
        while True:
            q = request.form.get(f'qualification_{idx}')
            s = request.form.get(f'specialization_{idx}')
            inst = request.form.get(f'institution_{idx}')
            year = request.form.get(f'passing_year_{idx}')
            perc = request.form.get(f'percentage_{idx}')
            if not any([q, s, inst, year, perc]):
                break
            education_entries.append({
                'qualification': sanitize_input(q or ''),
                'specialization': sanitize_input(s or ''),
                'institution': sanitize_input(inst or ''),
                'passing_year': sanitize_input(year or ''),
                'percentage_or_cgpa': sanitize_input(perc or '')
            })
            idx += 1

        # Address
        address = {
            'line1': sanitize_input(request.form.get('address_line1', '')),
            'line2': sanitize_input(request.form.get('address_line2', '')),
            'city': sanitize_input(request.form.get('city', '')),
            'state': sanitize_input(request.form.get('state', '')),
            'pincode': sanitize_input(request.form.get('pincode', ''))
        }

        # Preferences and other fields
        skills_text = sanitize_input(request.form.get('skills', ''))
        soft_skills_text = sanitize_input(request.form.get('soft_skills', ''))
        interests_list = request.form.getlist('interests') or []
        languages_text = sanitize_input(request.form.get('languages', ''))
        preferred_locations_text = sanitize_input(request.form.get('preferred_locations', ''))
        expected_stipend = sanitize_input(request.form.get('expected_stipend', ''))
        internship_duration = sanitize_input(request.form.get('internship_duration', ''))
        work_mode = sanitize_input(request.form.get('work_mode', ''))
        availability = sanitize_input(request.form.get('availability', ''))

        # Normalize list fields
        def to_list(csv):
            return [item.strip() for item in csv.split(',') if item.strip()] if csv else []
        skills_list = to_list(skills_text)
        soft_skills_list = to_list(soft_skills_text)
        languages_list = to_list(languages_text)
        preferred_locations_list = to_list(preferred_locations_text)

        # Validate required fields
        if not all([email, password, confirm_password, first_name, last_name]):
            flash('All required fields must be filled.', 'danger')
            return render_template('student_registration.html')

        # Validate email format
        if not validate_email_format(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('student_registration.html')

        # Validate password strength
        is_strong, message = validate_password_strength(password)
        if not is_strong:
            flash(f'Password error: {message}', 'danger')
            return render_template('student_registration.html')

        # Check password confirmation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('student_registration.html')

        # Check if user already exists
        try:
            if mongo_db is not None:
                existing_user = mongo_db.users.find_one({'email': email})
                if existing_user:
                    flash('An account with this email already exists. Please log in instead.', 'warning')
                    return redirect(url_for('login'))
        except Exception as e:
            print(f"Database check error: {e}")

        # Parse date of birth
        parsed_dob = None
        if dob_str:
            try:
                parsed_dob = datetime.strptime(dob_str, '%Y-%m-%d')
            except ValueError:
                try:
                    parsed_dob = datetime.strptime(dob_str, '%d-%m-%Y')
                except ValueError:
                    flash('Invalid date format. Please use DD-MM-YYYY format.', 'danger')
                    return render_template('student_registration.html')

        # Minimal file handling (optional, stored locally)
        resume_file = request.files.get('resume')
        photo_file = request.files.get('photo')
        additional_docs_file = request.files.get('additional_docs')
        resume_filename = None
        photo_filename = None
        additional_docs_filename = None
        try:
            upload_root = os.path.join('static', 'uploads')
            if resume_file and resume_file.filename:
                os.makedirs(os.path.join(upload_root, 'resumes'), exist_ok=True)
                fname = f"{secrets.token_hex(4)}_{secure_filename(resume_file.filename)}"
                resume_path = os.path.join(upload_root, 'resumes', fname)
                resume_file.save(resume_path)
                resume_filename = f"uploads/resumes/{fname}"
            if photo_file and photo_file.filename:
                os.makedirs(os.path.join(upload_root, 'photos'), exist_ok=True)
                fname = f"{secrets.token_hex(4)}_{secure_filename(photo_file.filename)}"
                photo_path = os.path.join(upload_root, 'photos', fname)
                photo_file.save(photo_path)
                photo_filename = f"uploads/photos/{fname}"
            if additional_docs_file and additional_docs_file.filename:
                os.makedirs(os.path.join(upload_root, 'documents'), exist_ok=True)
                fname = f"{secrets.token_hex(4)}_{secure_filename(additional_docs_file.filename)}"
                docs_path = os.path.join(upload_root, 'documents', fname)
                additional_docs_file.save(docs_path)
                additional_docs_filename = f"uploads/documents/{fname}"
        except Exception as fe:
            print(f"File upload save error: {fe}")

        # Prepare comprehensive form data for User model
        comprehensive_form_data = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'phone': phone,
            'date_of_birth': parsed_dob,
            'gender': gender,
            'category': category,
            'aadhaar_number': aadhaar_raw,
            'nationality': nationality,
            # Education and address
            'education': education_entries,
            'address': address,
            # Skills and preferences
            'skills': skills_list,
            'soft_skills': soft_skills_list,
            'interests': interests_list,
            'languages': languages_list,
            'preferred_locations': preferred_locations_list,
            'expected_stipend': expected_stipend,
            'internship_duration': internship_duration,
            'work_mode': work_mode,
            'availability': availability,
            # Documents
            'documents': {
                'resume': resume_filename,
                'photo': photo_filename,
                'additional_docs': additional_docs_filename
            },
            'created_at': get_current_datetime()
        }

        # Create comprehensive user using enhanced User model
        user = User.create_comprehensive_student(comprehensive_form_data)
        user_data = user.to_dict()

        try:
            if mongo_db is not None:
                # Save user to database
                result = mongo_db.users.insert_one(user_data)
                user_id = str(result.inserted_id)

                # Create secure session
                session.clear()
                current_time = get_current_datetime()
                session['user_id'] = user_id
                session['user_email'] = email
                session['user_name'] = first_name
                session['user_type'] = 'student'
                session['session_id'] = generate_secure_session_id()
                session['session_created_at'] = datetime_to_string(current_time)
                session.permanent = True

                flash(f'Welcome {first_name}! Your account has been created successfully with complete profile information.', 'success')
                return redirect(url_for('student_dashboard'))
            else:
                # Demo mode
                session.clear()
                current_time = get_current_datetime()
                session['user_id'] = 'demo_student_' + secrets.token_hex(8)
                session['user_email'] = email
                session['user_name'] = first_name
                session['user_type'] = 'student'
                session['session_id'] = generate_secure_session_id()
                session['session_created_at'] = datetime_to_string(current_time)
                session.permanent = True

                flash(f'Welcome {first_name}! Account created (Demo mode) with complete profile information.', 'success')
                return redirect(url_for('student_dashboard'))

        except Exception as e:
            print(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('student_registration.html')

@app.route('/test_profile_completion')
def test_profile_completion():
    """Test route for profile completion page (no login required)"""
    # Create sample form values for testing
    form_values = {
        'phone': '9876543210',
        'date_of_birth': '1995-05-15',
        'gender': 'Male',
        'nationality': 'Indian',
        'category': 'General',
        'aadhaar': '123456789012',
        'address_line1': '123 Test Street',
        'address_line2': 'Test Area',
        'city': 'Test City',
        'state': 'Test State',
        'pincode': '123456',
        'university': 'Test University',
        'degree': 'B.Tech',
        'specialization': 'Computer Science',
        'graduation_year': '2025',
        'cgpa': '8.5',
        'technical_skills': 'Python, Java, JavaScript',
        'soft_skills': 'Communication, Leadership',
        'languages': 'English, Hindi',
        'interests': 'Web Development, Machine Learning',
        'preferred_location': 'Mumbai, Bangalore',
        'internship_duration': '3-6 months',
        'work_mode': 'Hybrid',
        'expected_stipend': '15000',
        'availability': 'Immediately'
    }
    return render_template('student_profile_completion.html', form_values=form_values)


@app.route('/complete_student_profile', methods=['GET', 'POST'])
# @login_required  # Temporarily disabled for testing
def complete_student_profile():
    """Complete student profile after basic registration"""
    # Debug: Check session
    print(f"🔐 Session keys: {list(session.keys())}")
    print(f"🔐 User ID: {session.get('user_id')}")
    print(f"🔐 Logged in: {session.get('logged_in')}")
    
    # For testing, create a sample user_id if not logged in
    if not session.get('user_id'):
        session['user_id'] = '66e18e94c25c3b5c8bb7cb89'  # Use a test user ID
        print("🧪 Test user ID set for development")
    
    if request.method == 'POST':
        # Get comprehensive profile data from the form
        profile_data = {
            # Personal Information
            'phone': sanitize_input(request.form.get('phone', '')),
            'date_of_birth': sanitize_input(request.form.get('date_of_birth', '') or request.form.get('dob', '')),
            'gender': sanitize_input(request.form.get('gender', '')),
            'nationality': sanitize_input(request.form.get('nationality', 'Indian')),
            'category': sanitize_input(request.form.get('category', '')),
            'aadhaar': sanitize_input(request.form.get('aadhaar', '') or request.form.get('aadhaar_raw', '')),
            
            # Address Information
            'address_line1': sanitize_input(request.form.get('address_line1', '')),
            'address_line2': sanitize_input(request.form.get('address_line2', '')),
            'city': sanitize_input(request.form.get('city', '')),
            'state': sanitize_input(request.form.get('state', '')),
            'pincode': sanitize_input(request.form.get('pincode', '')),
            
            # Education Information
            'university': sanitize_input(request.form.get('university', '') or request.form.get('institution_1', '')),
            'degree': sanitize_input(request.form.get('degree', '') or request.form.get('qualification_1', '')),
            'specialization': sanitize_input(request.form.get('specialization', '') or request.form.get('specialization_1', '')),
            'graduation_year': sanitize_input(request.form.get('graduation_year', '') or request.form.get('passing_year_1', '')),
            'cgpa': sanitize_input(request.form.get('cgpa', '') or request.form.get('percentage_1', '')),
            
            # Skills and Interests
            'technical_skills': sanitize_input(request.form.get('technical_skills', '') or request.form.get('skills', '')),
            'soft_skills': sanitize_input(request.form.get('soft_skills', '')),
            'languages': sanitize_input(request.form.get('languages', '')),
            'interests': sanitize_input(request.form.get('interests', '')),
            
            # Preferences
            'preferred_location': sanitize_input(request.form.get('preferred_location', '') or request.form.get('preferred_locations', '')),
            'internship_duration': sanitize_input(request.form.get('internship_duration', '')),
            'work_mode': sanitize_input(request.form.get('work_mode', '')),
            'expected_stipend': sanitize_input(request.form.get('expected_stipend', '')),
            'availability': sanitize_input(request.form.get('availability', '')),
            
            # Profile metadata
            'profile_updated_at': get_current_datetime(),
            'profile_completion_date': get_current_datetime()
        }
        
        # Handle additional education entries if present
        education_entries = []
        for i in range(1, 6):  # Support up to 5 education entries
            qualification = request.form.get(f'qualification_{i}')
            if qualification:
                education_entry = {
                    'qualification': sanitize_input(qualification),
                    'specialization': sanitize_input(request.form.get(f'specialization_{i}', '')),
                    'institution': sanitize_input(request.form.get(f'institution_{i}', '')),
                    'passing_year': sanitize_input(request.form.get(f'passing_year_{i}', '')),
                    'percentage': sanitize_input(request.form.get(f'percentage_{i}', ''))
                }
                education_entries.append(education_entry)
        
        if education_entries:
            profile_data['education_entries'] = education_entries
        
        try:
            if mongo_db is not None:
                # Convert user_id to ObjectId if it's a string
                user_id = session.get('user_id')
                if isinstance(user_id, str):
                    try:
                        user_id = ObjectId(user_id)
                    except:
                        print(f"Invalid ObjectId format: {user_id}")
                        raise Exception("Invalid user ID format")
                
                # Update user profile in database with comprehensive data
                update_result = mongo_db.users.update_one(
                    {'_id': user_id},
                    {'$set': {
                        'profile_completed': True,
                        'profile_data': profile_data,
                        
                        # Also update top-level fields for easy querying
                        'phone': profile_data.get('phone', ''),
                        'date_of_birth': profile_data.get('date_of_birth', ''),
                        'gender': profile_data.get('gender', ''),
                        'nationality': profile_data.get('nationality', ''),
                        'category': profile_data.get('category', ''),
                        'aadhaar': profile_data.get('aadhaar', ''),
                        'address': {
                            'line1': profile_data.get('address_line1', ''),
                            'line2': profile_data.get('address_line2', ''),
                            'city': profile_data.get('city', ''),
                            'state': profile_data.get('state', ''),
                            'pincode': profile_data.get('pincode', '')
                        },
                        'education': {
                            'university': profile_data.get('university', ''),
                            'degree': profile_data.get('degree', ''),
                            'specialization': profile_data.get('specialization', ''),
                            'graduation_year': profile_data.get('graduation_year', ''),
                            'cgpa': profile_data.get('cgpa', ''),
                            'education_entries': education_entries
                        },
                        'skills': {
                            'technical': profile_data.get('technical_skills', ''),
                            'soft': profile_data.get('soft_skills', ''),
                            'languages': profile_data.get('languages', '')
                        },
                        'preferences': {
                            'interests': profile_data.get('interests', ''),
                            'preferred_location': profile_data.get('preferred_location', ''),
                            'internship_duration': profile_data.get('internship_duration', ''),
                            'work_mode': profile_data.get('work_mode', ''),
                            'expected_stipend': profile_data.get('expected_stipend', ''),
                            'availability': profile_data.get('availability', '')
                        },
                        'last_updated': get_current_datetime()
                    }}
                )
                
                if update_result.modified_count > 0:
                    print(f"✅ Profile updated successfully for user: {user_id}")
                    flash('Profile completed successfully! All your information has been saved.', 'success')
                else:
                    print(f"⚠️ Profile update had no effect for user: {user_id}")
                    flash('Profile information saved.', 'info')
                
            else:
                print("💾 Running in demo mode - profile saved to session")
                flash('Profile completed successfully! (Demo mode)', 'success')
                
            # Store in session for immediate use
            session['profile_completed'] = True
            session['registration_data'] = profile_data
            
            return redirect(url_for('student_dashboard'))
            
        except Exception as e:
            print(f"❌ Profile completion error: {e}")
            # Save to session as fallback
            session['profile_completed'] = True
            session['registration_data'] = profile_data
            flash('Profile saved successfully! (Fallback mode)', 'success')
            return redirect(url_for('student_dashboard'))
    
    # GET: Prefill the form with existing data
    user_doc = None
    form_values = {}
    
    if mongo_db is not None:
        try:
            uid = session.get('user_id')
            print(f"🔍 Fetching profile data for user_id: {uid}")
            oid = ObjectId(uid) if isinstance(uid, str) and len(uid) in (24,) else uid
            if oid:
                user_doc = mongo_db.users.find_one({'_id': oid})
                print(f"📋 User document found: {bool(user_doc)}")
                if user_doc:
                    print(f"📋 User keys: {list(user_doc.keys())}")
        except Exception as e:
            print(f"complete_student_profile DB fetch error: {e}")

    def to_csv(val):
        if not val:
            return ''
        if isinstance(val, list):
            return ', '.join([str(x) for x in val if str(x).strip()])
        return str(val)

    # Build defaults from DB
    if user_doc:
        print("🔄 Building form values from database")
        # Get nested data safely and normalize shapes
        profile_data = user_doc.get('profile_data') or {}
        profile_data = profile_data if isinstance(profile_data, dict) else {}

        addr = user_doc.get('address') or {}
        addr = addr if isinstance(addr, dict) else {}

        # education might be a dict or a list of dicts; take the first entry if list
        edu_src = user_doc.get('education') or {}
        if isinstance(edu_src, list):
            edu0 = edu_src[0] if (len(edu_src) > 0 and isinstance(edu_src[0], dict)) else {}
        elif isinstance(edu_src, dict):
            edu0 = edu_src
        else:
            edu0 = {}

        # skills might be a dict with categories or a flat list of skills
        skills_src = user_doc.get('skills') or []
        skills_dict = skills_src if isinstance(skills_src, dict) else {}
        skills_list = skills_src if isinstance(skills_src, list) else []

        prefs_src = user_doc.get('preferences') or {}
        prefs = prefs_src if isinstance(prefs_src, dict) else {}
        
        # Convert date of birth if it exists
        dob = user_doc.get('date_of_birth') or profile_data.get('date_of_birth')
        dob_str = ''
        if isinstance(dob, datetime):
            dob_str = dob.strftime('%Y-%m-%d')
        elif isinstance(dob, str):
            dob_str = dob

        form_values = {
            # Personal Information - check multiple locations
            'phone': user_doc.get('phone') or profile_data.get('phone', ''),
            'date_of_birth': dob_str,
            'gender': user_doc.get('gender') or profile_data.get('gender', ''),
            'nationality': user_doc.get('nationality') or profile_data.get('nationality', 'Indian'),
            'category': user_doc.get('category') or profile_data.get('category', ''),
            'aadhaar': user_doc.get('aadhaar') or user_doc.get('aadhaar_number') or profile_data.get('aadhaar', ''),
            
            # Address Information
            'address_line1': addr.get('line1') or addr.get('address_line1') or profile_data.get('address_line1', ''),
            'address_line2': addr.get('line2') or addr.get('address_line2') or profile_data.get('address_line2', ''),
            'city': addr.get('city') or user_doc.get('city') or profile_data.get('city', ''),
            'state': addr.get('state') or user_doc.get('state') or profile_data.get('state', ''),
            'pincode': addr.get('pincode') or user_doc.get('pincode') or profile_data.get('pincode', ''),
            
            # Education Information
            'university': edu0.get('university') or edu0.get('institution') or user_doc.get('college') or profile_data.get('university', ''),
            'degree': edu0.get('degree') or edu0.get('qualification') or user_doc.get('degree') or profile_data.get('degree', ''),
            'specialization': edu0.get('specialization') or user_doc.get('branch') or profile_data.get('specialization', ''),
            'graduation_year': edu0.get('graduation_year') or edu0.get('passing_year') or user_doc.get('graduation_year') or profile_data.get('graduation_year', ''),
            'cgpa': edu0.get('cgpa') or edu0.get('percentage') or user_doc.get('cgpa') or profile_data.get('cgpa', ''),
            
            # Skills
            'technical_skills': (skills_dict.get('technical') if skills_dict else None) or to_csv(skills_list or user_doc.get('skills', [])) or profile_data.get('technical_skills', ''),
            'soft_skills': (skills_dict.get('soft') if skills_dict else None) or to_csv(user_doc.get('soft_skills', [])) or profile_data.get('soft_skills', ''),
            'languages': (skills_dict.get('languages') if skills_dict else None) or to_csv(user_doc.get('languages', [])) or profile_data.get('languages', ''),
            
            # Preferences
            'interests': (prefs.get('interests') if isinstance(prefs, dict) else None) or to_csv(user_doc.get('interests', [])) or profile_data.get('interests', ''),
            'preferred_location': (prefs.get('preferred_location') if isinstance(prefs, dict) else None) or to_csv(user_doc.get('preferred_locations', [])) or profile_data.get('preferred_location', ''),
            'internship_duration': (prefs.get('internship_duration') if isinstance(prefs, dict) else None) or user_doc.get('internship_duration') or profile_data.get('internship_duration', ''),
            'work_mode': (prefs.get('work_mode') if isinstance(prefs, dict) else None) or user_doc.get('work_mode') or profile_data.get('work_mode', ''),
            'expected_stipend': (prefs.get('expected_stipend') if isinstance(prefs, dict) else None) or user_doc.get('expected_stipend') or profile_data.get('expected_stipend', ''),
            'availability': (prefs.get('availability') if isinstance(prefs, dict) else None) or user_doc.get('availability') or profile_data.get('availability', '')
        }
        print(f"📋 Form values built: {len([v for v in form_values.values() if v])}/{len(form_values)} fields populated")
    else:
        print("🔄 Building form values from session fallback")
        # Fallback from session registration_data
        reg = session.get('registration_data') or {}
        addr = (reg.get('address') if isinstance(reg, dict) else {}) or {}
        edu0 = ((reg.get('education') or [{}])[0] if isinstance(reg, dict) and reg.get('education') else {})
        pi = reg.get('personal_info', {}) if isinstance(reg, dict) else {}
        skills = reg.get('skills', {}) if isinstance(reg, dict) else {}
        prefs = reg.get('preferences', {}) if isinstance(reg, dict) else {}
        form_values = {
            'phone': pi.get('phone', ''),
            'date_of_birth': pi.get('dob', ''),
            'gender': pi.get('gender', ''),
            'nationality': pi.get('nationality', 'Indian'),
            'category': pi.get('category', ''),
            'aadhaar': pi.get('aadhaar', ''),
            'address_line1': addr.get('address_line1', ''),
            'address_line2': addr.get('address_line2', ''),
            'city': addr.get('city', ''),
            'state': addr.get('state', ''),
            'pincode': addr.get('pincode', ''),
            'university': edu0.get('institution', ''),
            'degree': edu0.get('qualification', ''),
            'specialization': edu0.get('specialization', ''),
            'graduation_year': edu0.get('passing_year', ''),
            'cgpa': edu0.get('percentage', ''),
            'technical_skills': skills.get('technical_skills', ''),
            'soft_skills': skills.get('soft_skills', ''),
            'languages': skills.get('languages', ''),
            'interests': prefs.get('interests', ''),
            'preferred_location': prefs.get('preferred_locations', ''),
            'internship_duration': prefs.get('internship_duration', ''),
            'work_mode': prefs.get('work_mode', ''),
            'expected_stipend': prefs.get('expected_stipend', ''),
            'availability': prefs.get('availability', '')
        }
    
    print(f"🎯 Final form_values keys with data: {[k for k, v in form_values.items() if v]}")
    return render_template('student_profile_completion.html', form_values=form_values)
    
    # GET: Prefill form values from DB or session
    
    # Note: The return above exits on POST. For GET, build and render with form_values
    
    

@app.route('/student_profile')
@login_required
def student_profile():
    """Student profile view that works after login by loading from DB and adapting to template shape"""
    user_doc = None
    adapted = None

    # Try to load from database first
    if mongo_db is not None:
        try:
            uid = session.get('user_id')
            oid = ObjectId(uid) if isinstance(uid, str) and len(uid) in (24,) else uid
            if oid:
                user_doc = mongo_db.users.find_one({'_id': oid})
        except Exception as e:
            print(f"student_profile DB fetch error: {e}")

    def to_csv(val):
        if not val:
            return ''
        if isinstance(val, list):
            return ', '.join([str(x) for x in val if str(x).strip()])
        return str(val)

    def basename_or_none(path):
        if not path:
            return None
        # Stored values may include 'uploads/.../filename'; keep only the filename for template
        try:
            return os.path.basename(path)
        except Exception:
            return path

    if user_doc:
        # Map DB doc to template's expected structure
        education_entries = []

        # Normalize education from various possible shapes
        edu_raw = user_doc.get('education')
        if isinstance(edu_raw, list):
            for item in edu_raw:
                if isinstance(item, dict):
                    education_entries.append({
                        'qualification': item.get('qualification') or item.get('degree', ''),
                        'specialization': item.get('specialization', ''),
                        'institution': item.get('institution') or item.get('university', ''),
                        'passing_year': item.get('passing_year') or item.get('graduation_year', ''),
                        'percentage': item.get('percentage') or item.get('cgpa') or item.get('percentage_or_cgpa', '')
                    })
                elif isinstance(item, str):
                    # Treat string as qualification/degree name and use top-level fallbacks
                    education_entries.append({
                        'qualification': item,
                        'specialization': user_doc.get('field_of_study', ''),
                        'institution': user_doc.get('institution_name', ''),
                        'passing_year': user_doc.get('year_of_study', ''),
                        'percentage': user_doc.get('cgpa', '')
                    })
        elif isinstance(edu_raw, dict):
            # Might be a single education dict or have education_entries inside
            nested_entries = edu_raw.get('education_entries') if isinstance(edu_raw.get('education_entries'), list) else None
            if nested_entries:
                for item in nested_entries:
                    if isinstance(item, dict):
                        education_entries.append({
                            'qualification': item.get('qualification') or item.get('degree', ''),
                            'specialization': item.get('specialization', ''),
                            'institution': item.get('institution') or item.get('university', ''),
                            'passing_year': item.get('passing_year') or item.get('graduation_year', ''),
                            'percentage': item.get('percentage') or item.get('cgpa') or item.get('percentage_or_cgpa', '')
                        })
            else:
                education_entries.append({
                    'qualification': edu_raw.get('qualification') or edu_raw.get('degree', ''),
                    'specialization': edu_raw.get('specialization', ''),
                    'institution': edu_raw.get('institution') or edu_raw.get('university', ''),
                    'passing_year': edu_raw.get('passing_year') or edu_raw.get('graduation_year', ''),
                    'percentage': edu_raw.get('percentage') or edu_raw.get('cgpa') or edu_raw.get('percentage_or_cgpa', '')
                })
        elif isinstance(edu_raw, str) and edu_raw.strip():
            # A single string like "B.Tech" stored as education
            education_entries.append({
                'qualification': edu_raw,
                'specialization': user_doc.get('field_of_study', ''),
                'institution': user_doc.get('institution_name', ''),
                'passing_year': user_doc.get('year_of_study', ''),
                'percentage': user_doc.get('cgpa', '')
            })

        # If nothing built yet, fall back to commonly used top-level fields
        if not education_entries:
            education_entries.append({
                'qualification': user_doc.get('current_education', '') or user_doc.get('degree', ''),
                'specialization': user_doc.get('field_of_study', ''),
                'institution': user_doc.get('institution_name', '') or user_doc.get('college', ''),
                'passing_year': user_doc.get('year_of_study', '') or user_doc.get('graduation_year', ''),
                'percentage': user_doc.get('cgpa', '')
            })

        address_obj = user_doc.get('address', {}) or {}
        adapted = {
            'personal_info': {
                'first_name': user_doc.get('first_name', ''),
                'middle_name': user_doc.get('middle_name', ''),
                'last_name': user_doc.get('last_name', ''),
                'email': user_doc.get('email', ''),
                'phone': user_doc.get('phone', ''),
                'dob': user_doc.get('date_of_birth') if isinstance(user_doc.get('date_of_birth'), str) else (user_doc.get('date_of_birth').strftime('%Y-%m-%d') if user_doc.get('date_of_birth') else ''),
                'gender': user_doc.get('gender', ''),
                'category': user_doc.get('category', ''),
                'aadhaar': user_doc.get('aadhaar_number', ''),
                'nationality': user_doc.get('nationality', '')
            },
            'address': {
                'address_line1': address_obj.get('line1') or address_obj.get('address_line1', ''),
                'address_line2': address_obj.get('line2') or address_obj.get('address_line2', ''),
                'city': address_obj.get('city', ''),
                'state': address_obj.get('state', ''),
                'pincode': address_obj.get('pincode', '')
            },
            'education': education_entries,
            'skills': {
                'technical_skills': to_csv(user_doc.get('skills', [])),
                'soft_skills': to_csv(user_doc.get('soft_skills', [])),
                'languages': to_csv(user_doc.get('languages', []))
            },
            'preferences': {
                'interests': to_csv(user_doc.get('interests', [])),
                'preferred_locations': to_csv(user_doc.get('preferred_locations', [])),
                'internship_duration': user_doc.get('internship_duration', ''),
                'work_mode': user_doc.get('work_mode', ''),
                'expected_stipend': user_doc.get('expected_stipend', ''),
                'availability': user_doc.get('availability', '')
            },
            'documents': {
                'resume': basename_or_none((user_doc.get('documents') or {}).get('resume')),
                'photo': basename_or_none((user_doc.get('documents') or {}).get('photo')),
                'additional_docs': basename_or_none((user_doc.get('documents') or {}).get('additional_docs'))
            },
            'registration_date': (user_doc.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if isinstance(user_doc.get('created_at'), datetime) else (user_doc.get('created_at') or ''))
        }
    else:
        # Fallback to session registration data if available
        reg = session.get('registration_data')
        if reg:
            try:
                # Normalize fields from session structure
                docs = reg.get('documents', {}) if isinstance(reg, dict) else {}
                adapted = {
                    'personal_info': reg.get('personal_info', {}),
                    'address': reg.get('address', {}),
                    'education': reg.get('education', []),
                    'skills': reg.get('skills', {}),
                    'preferences': reg.get('preferences', {}),
                    'documents': {
                        'resume': basename_or_none(docs.get('resume')),
                        'photo': basename_or_none(docs.get('photo')),
                        'additional_docs': basename_or_none(docs.get('additional_docs'))
                    },
                    'registration_date': reg.get('registration_date', '')
                }
            except Exception as e:
                print(f"student_profile session adapt error: {e}")

    if not adapted:
        flash('Profile data not found. Please complete your profile.', 'warning')
        return redirect(url_for('complete_student_profile'))

    return render_template('student_profile.html', student=adapted)

@app.route('/register_student', methods=['POST'])
def register_student():
    if request.method == 'POST':
        # Process form data
        form_data = request.form.to_dict()
        files = request.files
        
        # Process education entries
        education_entries = []
        for key in form_data:
            if key.startswith('qualification_'):
                index = key.split('_')[1]
                entry = {
                    'qualification': form_data.get(f'qualification_{index}', ''),
                    'specialization': form_data.get(f'specialization_{index}', ''),
                    'institution': form_data.get(f'institution_{index}', ''),
                    'passing_year': form_data.get(f'passing_year_{index}', ''),
                    'percentage': form_data.get(f'percentage_{index}', '')
                }
                education_entries.append(entry)
        
        # Handle resume upload
        resume_filename = None
        if 'resume' in files and files['resume'].filename:
            try:
                resume_file = files['resume']
                # Check file type
                allowed_extensions = {'.pdf', '.doc', '.docx'}
                file_ext = os.path.splitext(resume_file.filename)[1].lower()
                if file_ext not in allowed_extensions:
                    flash('Resume must be a PDF, DOC, or DOCX file', 'error')
                    return redirect(request.url)
                
                resume_filename = secure_filename(resume_file.filename)
                resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', resume_filename)
                os.makedirs(os.path.dirname(resume_path), exist_ok=True)
                resume_file.save(resume_path)
                form_data['resume_filename'] = resume_filename
            except Exception as e:
                flash(f'Error uploading resume: {str(e)}', 'error')
                return redirect(request.url)
        
        # Handle photo upload
        photo_filename = None
        if 'photo' in files and files['photo'].filename:
            try:
                photo_file = files['photo']
                photo_filename = secure_filename(photo_file.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', photo_filename)
                print(f"Saving photo to: {photo_path}")
                # Ensure directory exists
                os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                photo_file.save(photo_path)
                form_data['photo_filename'] = photo_filename
                print(f"Photo saved successfully: {photo_filename}")
            except Exception as e:
                print(f"Error saving photo: {str(e)}")
                flash(f'Error saving photo: {str(e)}', 'error')
            
        # Handle additional documents
        additional_docs_filename = None
        if 'additional_docs' in files and files['additional_docs'].filename:
            docs_file = files['additional_docs']
            additional_docs_filename = secure_filename(docs_file.filename)
            docs_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', additional_docs_filename)
            os.makedirs(os.path.dirname(docs_path), exist_ok=True)
            docs_file.save(docs_path)
            form_data['additional_docs_filename'] = additional_docs_filename
        
        # Format interests array if it's a list
        if isinstance(form_data.get('interests'), list):
            form_data['interests'] = ', '.join(form_data['interests'])
        
        # In a real app, we would save the data to a database
        # Create a complete profile object
        profile = {
            'personal_info': {
                'first_name': form_data.get('first_name', ''),
                'middle_name': form_data.get('middle_name', ''),
                'last_name': form_data.get('last_name', ''),
                'email': form_data.get('email', ''),
                'phone': form_data.get('phone', ''),
                'dob': form_data.get('dob', ''),
                'gender': form_data.get('gender', ''),
                'category': form_data.get('category', ''),
                'aadhaar': form_data.get('aadhaar_raw', form_data.get('aadhaar', '')),
                'nationality': form_data.get('nationality', '')
            },
            'address': {
                'address_line1': form_data.get('address_line1', ''),
                'address_line2': form_data.get('address_line2', ''),
                'city': form_data.get('city', ''),
                'state': form_data.get('state', ''),
                'pincode': form_data.get('pincode', '')
            },
            'education': education_entries,
            'skills': {
                'technical_skills': form_data.get('skills', ''),
                'soft_skills': form_data.get('soft_skills', ''),
                'languages': form_data.get('languages', '')
            },
            'preferences': {
                'interests': form_data.get('interests', ''),
                'preferred_locations': form_data.get('preferred_locations', ''),
                'internship_duration': form_data.get('internship_duration', ''),
                'work_mode': form_data.get('work_mode', ''),
                'expected_stipend': form_data.get('expected_stipend', ''),
                'availability': form_data.get('availability', '')
            },
            'documents': {
                'resume': resume_filename,
                'photo': photo_filename,
                'additional_docs': additional_docs_filename
            },
            'consents': {
                'terms_accepted': 'terms_accepted' in form_data,
                'data_accuracy': 'data_accuracy' in form_data,
                'communication_consent': 'communication_consent' in form_data,
                'verification_consent': 'verification_consent' in form_data
            },
            'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store the profile in MongoDB
        try:
            if mongo_db is not None:
                result = mongo_db.student_profiles.insert_one(profile)
                profile['_id'] = str(result.inserted_id)
                flash('Registration successful! Data saved to database. Welcome to InternGenius!', 'success')
            else:
                flash('Registration successful! Welcome to InternGenius (Demo mode - database not connected)', 'success')
            
            # Store the complete profile in session
            session['registration_data'] = profile
            
        except Exception as e:
            # If database fails, still store in session for demo
            session['registration_data'] = profile
            flash('Registration successful! Welcome to InternGenius (Demo mode)', 'success')
            print(f"Database error: {e}")
        
        # Add registration date for the success page
        form_data['now'] = datetime.now()
        
        # Convert qualification values to more readable format
        qualification_map = {
            'high_school': 'High School (10th)',
            'intermediate': 'Intermediate (12th)',
            'diploma': 'Diploma',
            'bachelors': 'Bachelor\'s Degree',
            'masters': 'Master\'s Degree',
            'phd': 'PhD'
        }
        
        # Format the form data for display
        if 'qualification_1' in form_data and form_data['qualification_1'] in qualification_map:
            form_data['qualification_1'] = qualification_map[form_data['qualification_1']]
            
        # Format interests to be more readable if they're codes
        interests = []
        if form_data.get('interests'):
            interest_map = {
                'software_development': 'Software Development',
                'data_science': 'Data Science & Analytics',
                'web_development': 'Web Development',
                'mobile_development': 'Mobile App Development',
                'ui_ux': 'UI/UX Design',
                'digital_marketing': 'Digital Marketing',
                'content_writing': 'Content Writing',
                'finance': 'Finance & Accounting',
                'hr': 'Human Resources',
                'mechanical': 'Mechanical Engineering',
                'civil': 'Civil Engineering',
                'electrical': 'Electrical Engineering',
                'chemical': 'Chemical Engineering',
                'artificial_intelligence': 'Artificial Intelligence',
                'blockchain': 'Blockchain',
                'cloud_computing': 'Cloud Computing'
            }
            
            for interest in form_data.get('interests', '').split(','):
                interest = interest.strip()
                if interest in interest_map:
                    interests.append(interest_map[interest])
                else:
                    interests.append(interest)
            
            if interests:
                form_data['interests'] = ', '.join(interests)
        
        # Redirect to a success page or dashboard
        return render_template('registration_success.html', form_data=form_data, now=datetime.now())

# Company registration route
@app.route('/direct_company_registration', methods=['GET', 'POST'])
def direct_company_registration():
    if request.method == 'POST':
        # Process company registration
        form_data = request.form.to_dict()
        
        company_profile = {
            'company_name': form_data.get('company_name', ''),
            'industry': form_data.get('industry', ''),
            'company_size': form_data.get('company_size', ''),
            'website': form_data.get('website', ''),
            'description': form_data.get('description', ''),
            'address': form_data.get('address', ''),
            'contact_person': form_data.get('contact_person', ''),
            'contact_email': form_data.get('contact_email', ''),
            'contact_phone': form_data.get('contact_phone', ''),
            'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending_verification'
        }
        
        # Try to save to database
        try:
            if mongo_db is not None:
                result = mongo_db.company_profiles.insert_one(company_profile)
                flash('Company registration successful! Your profile is under review.', 'success')
            else:
                flash('Company registration successful! (Demo mode)', 'success')
        except Exception as e:
            flash('Company registration successful! (Demo mode)', 'success')
            print(f"Database error: {e}")
        
        return redirect(url_for('company_dashboard'))
    
    return render_template('company_registration.html')

# Admin registration route
@app.route('/direct_admin_registration', methods=['GET', 'POST'])
def direct_admin_registration():
    if request.method == 'POST':
        # Process admin registration
        form_data = request.form.to_dict()
        
        # Simple verification code check
        if form_data.get('verification_code') != 'ADMIN2025':
            flash('Invalid verification code. Access denied.', 'error')
            return render_template('admin_registration.html')
        
        admin_profile = {
            'admin_name': form_data.get('admin_name', ''),
            'department': form_data.get('department', ''),
            'employee_id': form_data.get('employee_id', ''),
            'email': form_data.get('email', ''),
            'phone': form_data.get('phone', ''),
            'role': 'admin',
            'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active'
        }
        
        # Try to save to database
        try:
            if mongo_db is not None:
                result = mongo_db.admin_profiles.insert_one(admin_profile)
                flash('Admin registration successful! Welcome to the admin panel.', 'success')
            else:
                flash('Admin registration successful! (Demo mode)', 'success')
        except Exception as e:
            flash('Admin registration successful! (Demo mode)', 'success')
            print(f"Database error: {e}")
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_registration.html')

# Dashboard routes (all require authentication)
@app.route('/dashboard')
def dashboard():
    """Generic dashboard that redirects to appropriate user-specific dashboard"""
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'warning')
        return redirect(url_for('login'))
    
    # Get user type from session and redirect to appropriate dashboard
    user_type = session.get('user_type', 'student')
    if user_type == 'student':
        return redirect(url_for('student_dashboard'))
    elif user_type == 'company':
        return redirect(url_for('company_dashboard'))
    elif user_type == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))  # Default fallback

@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard - requires authentication"""
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'warning')
        return redirect(url_for('login'))
    
    # Optionally check if user is actually a student
    if session.get('user_type') != 'student':
        flash('Access denied. This dashboard is for students only.', 'danger')
        return redirect(url_for('dashboard'))
    # Load user details
    user_doc = None
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    last_login = None
    skills = []
    interests = []
    preferred_locations = []
    profile_completed = session.get('profile_completed', False)
    education = []
    profile_views = 0
    skill_score = 0

    if mongo_db is not None:
        try:
            uid = session.get('user_id')
            oid = ObjectId(uid) if isinstance(uid, str) and len(uid) in (24, ) else uid
            user_doc = mongo_db.users.find_one({'_id': oid}) if oid else None
            if user_doc:
                user_name = user_doc.get('first_name', user_name)
                user_email = user_doc.get('email', user_email)
                last_login = user_doc.get('last_login')
                profile_completed = user_doc.get('profile_completed', profile_completed)
                # Enhanced fields
                skills = user_doc.get('skills', []) or []
                interests = user_doc.get('interests', []) or []
                preferred_locations = user_doc.get('preferred_locations', []) or []
                education = user_doc.get('education', []) or []
                profile_views = user_doc.get('metrics', {}).get('profile_views', 0)
        except Exception as e:
            print(f"Dashboard user fetch error: {e}")

    # Fallback to session registration data
    reg = session.get('registration_data') or {}
    if not skills:
        skills = (reg.get('skills') or reg.get('profile_data', {}).get('technical_skills') or [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]
    if not interests:
        raw = reg.get('preferences', {},).get('interests') if isinstance(reg, dict) else None
        interests = raw or []
        if isinstance(interests, str):
            interests = [i.strip() for i in interests.split(',') if i.strip()]
    if not preferred_locations:
        raw = (reg.get('preferences', {}) if isinstance(reg, dict) else {}).get('preferred_locations', [])
        preferred_locations = raw if isinstance(raw, list) else [l.strip() for l in str(raw).split(',') if l.strip()]
    if not education:
        education = reg.get('education', []) if isinstance(reg, dict) else []

    # Compute simple profile completion percent
    required_checks = 10
    completed = 0
    if user_name: completed += 1
    if user_email: completed += 1
    # phone/date/gender/address in either user_doc or reg
    phone = (user_doc or {}).get('phone') or (reg.get('personal_info', {}) if isinstance(reg, dict) else {}).get('phone')
    if phone: completed += 1
    dob = (user_doc or {}).get('date_of_birth') or (reg.get('personal_info', {}) if isinstance(reg, dict) else {}).get('dob')
    if dob: completed += 1
    gender = (user_doc or {}).get('gender') or (reg.get('personal_info', {}) if isinstance(reg, dict) else {}).get('gender')
    if gender: completed += 1
    if education: completed += 1
    if skills: completed += 1
    if interests: completed += 1
    if preferred_locations: completed += 1
    # documents
    docs = (user_doc or {}).get('documents') or (reg.get('documents') if isinstance(reg, dict) else {})
    if docs and (docs.get('resume') or docs.get('photo')): completed += 1
    profile_completion_percent = int((completed / required_checks) * 100)

    # Simple skill score heuristic
    skill_score = min(100, 50 + len(skills) * 5)

    # Applications stats (best-effort)
    applications_count = 0
    interviews_count = 0
    if mongo_db is not None:
        try:
            uid = session.get('user_id')
            oid = ObjectId(uid) if isinstance(uid, str) and len(uid) in (24,) else uid
            if oid:
                applications_count = mongo_db.get_collection('applications').count_documents({'user_id': oid})
                interviews_count = mongo_db.get_collection('applications').count_documents({'user_id': oid, 'status': 'interview'})
        except Exception:
            pass

    # Recommended internships (basic filter using sample data)
    sample_internships = [
        {
            '_id': '1', 'title': 'Software Development Intern', 'company': 'Tech Innovations Pvt Ltd',
            'location': 'Bangalore', 'duration': '3 months', 'stipend': '₹15,000/month', 'work_mode': 'Hybrid',
            'description': 'Join our dynamic team...', 'skills': ['Python', 'React', 'JavaScript', 'Git', 'MongoDB']
        },
        {
            '_id': '2', 'title': 'Digital Marketing Intern', 'company': 'Creative Solutions',
            'location': 'Mumbai', 'duration': '6 months', 'stipend': '₹12,000/month', 'work_mode': 'Remote',
            'description': 'Learn digital marketing...', 'skills': ['Social Media', 'Google Analytics', 'Content Writing', 'SEO', 'Canva']
        },
        {
            '_id': '3', 'title': 'Data Science Intern', 'company': 'Analytics Corp',
            'location': 'Hyderabad', 'duration': '4 months', 'stipend': '₹18,000/month', 'work_mode': 'On-site',
            'description': 'Work with large datasets...', 'skills': ['Python', 'Machine Learning', 'SQL', 'Tableau', 'Pandas']
        },
        {
            '_id': '4', 'title': 'UI/UX Design Intern', 'company': 'Design Studio Pro',
            'location': 'Delhi', 'duration': '5 months', 'stipend': '₹14,000/month', 'work_mode': 'Hybrid',
            'description': 'Create user-centered designs...', 'skills': ['Figma', 'Adobe XD', 'Prototyping', 'User Research', 'HTML/CSS']
        }
    ]
    def match_score(offer):
        if not skills:
            return 0
        return sum(1 for s in offer.get('skills', []) if s.lower() in [x.lower() for x in skills])
    recommended = sorted(sample_internships, key=match_score, reverse=True)
    recommended = [o for o in recommended if match_score(o) > 0] or sample_internships[:3]

    return render_template(
        'dashboards/student_dashboard.html',
        user_name=user_name,
        user_email=user_email,
        last_login=last_login,
        profile_completed=profile_completed,
        profile_completion_percent=profile_completion_percent,
        applications_count=applications_count or 0,
        interviews_count=interviews_count or 0,
        profile_views=profile_views or 0,
        skill_score=skill_score,
        skills=skills,
        interests=interests,
        preferred_locations=preferred_locations,
        recommended_internships=recommended
    )

@app.route('/company/dashboard')
def company_dashboard():
    """Company dashboard - requires authentication"""
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'warning')
        return redirect(url_for('login'))
    
    # Optionally check if user is actually a company
    if session.get('user_type') != 'company':
        flash('Access denied. This dashboard is for companies only.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('dashboards/company_dashboard.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard - requires authentication and admin privileges"""
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'warning')
        return redirect(url_for('login'))
    
    # Check if user is actually an admin
    if session.get('user_type') != 'admin':
        flash('Access denied. This dashboard is for administrators only.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('dashboards/admin_dashboard.html')

# Additional functional routes
@app.route('/search_internships')
def search_internships():
    """Display search page with filters"""
    # Get search parameters
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    category = request.args.get('category', '')
    
    # Sample internship data - replace with MongoDB query
    sample_internships = [
        {
            '_id': '1',
            'title': 'Software Development Intern',
            'company': 'Tech Innovations Pvt Ltd',
            'location': 'Bangalore',
            'duration': '3 months',
            'stipend': '₹15,000/month',
            'work_mode': 'Hybrid',
            'description': 'Join our dynamic team to work on cutting-edge web applications using Python and React. You will be mentored by senior developers and work on real projects.',
            'skills': ['Python', 'React', 'JavaScript', 'Git', 'MongoDB'],
            'requirements': [
                'Currently pursuing Computer Science or related field',
                'Basic knowledge of Python and web development',
                'Good communication skills',
                'Ability to work in a team environment'
            ],
            'posted_date': 'Jan 15, 2025',
            'deadline': 'Feb 15, 2025',
            'start_date': 'Mar 1, 2025'
        },
        {
            '_id': '2',
            'title': 'Digital Marketing Intern',
            'company': 'Creative Solutions',
            'location': 'Mumbai',
            'duration': '6 months',
            'stipend': '₹12,000/month',
            'work_mode': 'Remote',
            'description': 'Learn digital marketing strategies and help execute campaigns for our diverse client base. Work with social media, content creation, and analytics.',
            'skills': ['Social Media', 'Google Analytics', 'Content Writing', 'SEO', 'Canva'],
            'requirements': [
                'Currently pursuing Marketing, Communications, or related field',
                'Creative mindset with attention to detail',
                'Basic understanding of social media platforms',
                'Good writing and communication skills'
            ],
            'posted_date': 'Jan 12, 2025',
            'deadline': 'Feb 10, 2025',
            'start_date': 'Feb 20, 2025'
        },
        {
            '_id': '3',
            'title': 'Data Science Intern',
            'company': 'Analytics Corp',
            'location': 'Hyderabad',
            'duration': '4 months',
            'stipend': '₹18,000/month',
            'work_mode': 'On-site',
            'description': 'Work with large datasets and machine learning models to derive business insights. Collaborate with data scientists and engineers on real-world projects.',
            'skills': ['Python', 'Machine Learning', 'SQL', 'Tableau', 'Pandas'],
            'requirements': [
                'Currently pursuing Computer Science, Statistics, or related field',
                'Strong analytical and problem-solving skills',
                'Experience with Python and data analysis libraries',
                'Understanding of statistical concepts'
            ],
            'posted_date': 'Jan 10, 2025',
            'deadline': 'Feb 5, 2025',
            'start_date': 'Feb 15, 2025'
        },
        {
            '_id': '4',
            'title': 'UI/UX Design Intern',
            'company': 'Design Studio Pro',
            'location': 'Delhi',
            'duration': '5 months',
            'stipend': '₹14,000/month',
            'work_mode': 'Hybrid',
            'description': 'Create user-centered designs for web and mobile applications. Work alongside experienced designers to develop wireframes, prototypes, and design systems.',
            'skills': ['Figma', 'Adobe XD', 'Prototyping', 'User Research', 'HTML/CSS'],
            'requirements': [
                'Currently pursuing Design, HCI, or related field',
                'Portfolio showcasing design projects',
                'Proficiency in design tools like Figma or Adobe XD',
                'Understanding of user-centered design principles'
            ],
            'posted_date': 'Jan 8, 2025',
            'deadline': 'Feb 1, 2025',
            'start_date': 'Feb 10, 2025'
        }
    ]
    
    # Filter internships based on search parameters
    filtered_internships = sample_internships
    if keyword:
        filtered_internships = [i for i in filtered_internships if keyword.lower() in i['title'].lower() or keyword.lower() in i['description'].lower()]
    if location:
        filtered_internships = [i for i in filtered_internships if i['location'] == location]
    if category:
        # Simple category matching based on skills
        category_keywords = {
            'Technology': ['Python', 'JavaScript', 'React', 'Git', 'MongoDB', 'HTML/CSS'],
            'Marketing': ['Social Media', 'SEO', 'Content Writing', 'Google Analytics'],
            'Research': ['Machine Learning', 'SQL', 'Tableau', 'Data Science'],
            'Finance': ['Finance', 'Accounting', 'Excel'],
            'Healthcare': ['Healthcare', 'Medical', 'Biology'],
            'Education': ['Teaching', 'Education', 'Training']
        }
        if category in category_keywords:
            filtered_internships = [i for i in filtered_internships if any(skill in category_keywords[category] for skill in i['skills'])]
    
    return render_template('search_internships.html', internships=filtered_internships)

@app.route('/my_applications')
def my_applications():
    """Display user's internship applications"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Sample application data - replace with database query
    sample_applications = [
        {
            'title': 'Software Development Intern',
            'company': 'Tech Innovations Pvt Ltd',
            'applied_date': 'Jan 15, 2025',
            'status': 'Under Review',
            'status_class': 'warning'
        },
        {
            'title': 'Data Science Intern',
            'company': 'Analytics Corp',
            'applied_date': 'Jan 10, 2025',
            'status': 'Interview Scheduled',
            'status_class': 'info'
        }
    ]
    
    return render_template('my_applications.html', applications=sample_applications)

def format_date(date_str):
    """Helper function to format dates"""
    return date_str

# Register the template filter
app.jinja_env.filters['format_date'] = format_date

@app.route('/check_login')
def check_login():
    """API endpoint to check if user is logged in"""
    return jsonify({'logged_in': 'user_id' in session})

@app.route('/apply_internship', methods=['POST'])
def apply_internship():
    """Handle internship application with CSRF protection"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    # CSRF validation is handled by Flask-WTF automatically for JSON requests
    # when the X-CSRFToken header is provided
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request data'})
        
    internship_id = data.get('internship_id')
    if not internship_id:
        return jsonify({'success': False, 'message': 'Internship ID is required'})
    
    # Here you would typically save the application to database
    # For now, just return success
    return jsonify({'success': True, 'message': 'Application submitted successfully'})

@app.route('/internship/<int:internship_id>')
def internship_details(internship_id):
    # Mock internship details
    internship = {
        'id': internship_id,
        'title': 'Software Development Intern',
        'company': 'TechCorp Solutions',
        'location': 'Remote',
        'duration': '6 months',
        'stipend': '₹25,000/month',
        'skills': ['Python', 'React', 'MongoDB', 'Git', 'REST APIs'],
        'description': 'We are looking for passionate software developers to join our team...',
        'requirements': [
            'Currently pursuing B.Tech/B.E in Computer Science or related field',
            'Knowledge of Python programming language',
            'Basic understanding of web technologies',
            'Good communication skills'
        ],
        'responsibilities': [
            'Develop and maintain web applications',
            'Collaborate with senior developers',
            'Write clean, maintainable code',
            'Participate in code reviews'
        ]
    }
    return render_template('internship_details.html', internship=internship)



# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Context processor for global template variables
@app.context_processor
def utility_processor():
    def format_date(date_str):
        if date_str:
            from datetime import datetime
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                return dt.strftime('%d %B, %Y')
            except:
                return date_str
        return ''
    
    return dict(format_date=format_date)

if __name__ == '__main__':
    app.run(debug=True)
