from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User
from app import mongo, csrf
from forms.auth_forms import LoginForm, SignupForm
from forms.profile_forms import StudentProfileForm, CompanyProfileForm, AdminProfileForm
from werkzeug.utils import secure_filename
import os
import uuid
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        password = form.password.data
        
        user = User.get_by_email(email, mongo)
        
        if user and user.check_password(password):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.get_full_name()}!', 'success')
            
            # Redirect to appropriate dashboard
            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'company':
                return redirect(url_for('company.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/signup')
def signup():
    """Redirect to role selection page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Always redirect to role selection page
    return render_template('auth/role_selection.html')

@auth_bp.route('/register/student', methods=['GET', 'POST'])
def student_registration():
    """Student profile completion route."""
    # Check if user has completed the first registration step
    if 'user_data' not in session:
        flash('Please complete the basic registration first.', 'warning')
        return redirect(url_for('auth.signup', role='student'))
    
    form = StudentProfileForm()
    
    if form.validate_on_submit():
        # Get the basic user data from session
        user_data = session.pop('user_data')
        
        # Create user document with extended profile info
        user = {
            'email': user_data['email'],
            'password': user_data['password'],  # Will be hashed in User.create
            'role': 'student',
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'profile': {
                'institution': form.institution.data,
                'degree': form.degree.data,
                'field_of_study': form.field_of_study.data,
                'graduation_year': form.graduation_year.data,
                'phone': form.phone.data,
                'city': form.city.data,
                'state': form.state.data,
                'skills': [skill.strip() for skill in form.skills.data.split(',')],
                'interests': [interest.strip() for interest in form.interests.data.split(',')],
                'bio': form.bio.data,
                'linkedin': form.linkedin.data,
                'github': form.github.data,
                'portfolio': form.portfolio.data,
                'notifications_enabled': form.notifications.data,
                'profile_completed': True,
                'created_at': datetime.datetime.utcnow()
            }
        }
        
        # Handle resume upload
        if form.resume.data:
            filename = secure_filename(f"{uuid.uuid4()}_{form.resume.data.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            form.resume.data.save(filepath)
            user['profile']['resume_path'] = filepath
        
        # Create the user with the extended profile
        user_id = User.create(user, mongo)
        
        # Log the user in
        user_obj = User.get_by_id(user_id, mongo)
        login_user(user_obj)
        
        flash('Your student profile has been created successfully!', 'success')
        return redirect(url_for('student.dashboard'))
    
    return render_template('auth/student_registration.html', form=form)

@auth_bp.route('/register/company', methods=['GET', 'POST'])
def company_registration():
    """Company profile completion route."""
    # Check if user has completed the first registration step
    if 'user_data' not in session:
        flash('Please complete the basic registration first.', 'warning')
        return redirect(url_for('auth.signup', role='company'))
    
    form = CompanyProfileForm()
    
    if form.validate_on_submit():
        # Get the basic user data from session
        user_data = session.pop('user_data')
        
        # Create user document with extended profile info
        user = {
            'email': user_data['email'],
            'password': user_data['password'],  # Will be hashed in User.create
            'role': 'company',
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'profile': {
                'company_name': form.company_name.data,
                'industry': form.industry.data,
                'company_size': form.company_size.data,
                'contact_person': form.contact_person.data,
                'contact_position': form.contact_position.data,
                'contact_email': form.contact_email.data,
                'phone': form.phone.data,
                'headquarters': form.headquarters.data,
                'website': form.website.data,
                'description': form.company_description.data,
                'linkedin': form.linkedin.data,
                'verification_status': 'pending',  # Admin needs to verify company
                'profile_completed': True,
                'created_at': datetime.datetime.utcnow()
            }
        }
        
        # Handle logo upload
        if form.logo.data:
            logo_filename = secure_filename(f"{uuid.uuid4()}_{form.logo.data.filename}")
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'company_logos', logo_filename)
            os.makedirs(os.path.dirname(logo_path), exist_ok=True)
            form.logo.data.save(logo_path)
            user['profile']['logo_path'] = logo_path
        
        # Handle registration document upload
        if form.registration_document.data:
            doc_filename = secure_filename(f"{uuid.uuid4()}_{form.registration_document.data.filename}")
            doc_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'company_documents', doc_filename)
            os.makedirs(os.path.dirname(doc_path), exist_ok=True)
            form.registration_document.data.save(doc_path)
            user['profile']['registration_document_path'] = doc_path
        
        # Create the user with the extended profile
        user_id = User.create(user, mongo)
        
        # Log the user in
        user_obj = User.get_by_id(user_id, mongo)
        login_user(user_obj)
        
        flash('Your company profile has been created. It will be reviewed for verification shortly.', 'success')
        return redirect(url_for('company.dashboard'))
    
    return render_template('auth/company_registration.html', form=form)

@auth_bp.route('/register/admin', methods=['GET', 'POST'])
def admin_registration():
    """Administrator profile completion route."""
    # Check if user has completed the first registration step
    if 'user_data' not in session:
        flash('Please complete the basic registration first.', 'warning')
        return redirect(url_for('auth.signup', role='admin'))
    
    form = AdminProfileForm()
    
    if form.validate_on_submit():
        # Get the basic user data from session
        user_data = session.pop('user_data')
        
        # Create user document with extended profile info
        user = {
            'email': user_data['email'],
            'password': user_data['password'],  # Will be hashed in User.create
            'role': 'admin',
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'profile': {
                'admin_id': form.admin_id.data,
                'department': form.department.data,
                'phone': form.phone.data,
                'alternate_email': form.alternate_email.data,
                'security_question': form.security_question.data,
                'security_answer': form.security_answer.data,  # Should be hashed in production
                'permissions': form.permissions.data,
                'verification_status': 'pending',  # Super admin needs to verify
                'profile_completed': True,
                'created_at': datetime.datetime.utcnow()
            }
        }
        
        # Handle admin document upload
        if form.admin_verification_document.data:
            filename = secure_filename(f"{uuid.uuid4()}_{form.admin_verification_document.data.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'admin_documents', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            form.admin_verification_document.data.save(filepath)
            user['profile']['verification_document_path'] = filepath
        
        # Create the user with the extended profile
        user_id = User.create(user, mongo)
        
        # Log the user in
        user_obj = User.get_by_id(user_id, mongo)
        login_user(user_obj)
        
        flash('Your administrator profile has been created. It requires verification by a super admin.', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('auth/admin_registration.html', form=form)

@auth_bp.route('/student', methods=['GET', 'POST'])
def direct_student_registration():
    """Direct student registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Create a form instance
    form = SignupForm()
    # Set the default role and process form
    form.role.data = 'student'
        
    if form.validate_on_submit():
        # Get form data
        email = form.email.data.lower().strip()
        password = form.password.data
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        
        # Check if user already exists
        if User.email_exists(email, mongo):
            flash('Email already registered. Please use a different email or login.', 'error')
            return render_template('auth/student_direct.html', form=form)
        
        # Store user data in session
        session['user_data'] = {
            'email': email,
            'password': password,
            'role': 'student',
            'first_name': first_name,
            'last_name': last_name
        }
        
        return redirect(url_for('auth.student_registration'))
        
    return render_template('auth/student_direct.html', form=form)

@auth_bp.route('/company', methods=['GET', 'POST'])
def direct_company_registration():
    """Direct company registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Create a form instance
    form = SignupForm()
    # Set the default role and process form
    form.role.data = 'company'
        
    if form.validate_on_submit():
        # Get form data
        email = form.email.data.lower().strip()
        password = form.password.data
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        
        # Check if user already exists
        if User.email_exists(email, mongo):
            flash('Email already registered. Please use a different email or login.', 'error')
            return render_template('auth/company_direct.html', form=form)
        
        # Store user data in session
        session['user_data'] = {
            'email': email,
            'password': password,
            'role': 'company',
            'first_name': first_name,
            'last_name': last_name
        }
        
        return redirect(url_for('auth.company_registration'))
    
    return render_template('auth/company_direct.html', form=form)

@auth_bp.route('/admin', methods=['GET', 'POST'])
def direct_admin_registration():
    """Direct admin registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Create a form instance
    form = SignupForm()
    # Set the default role and process form
    form.role.data = 'admin'
        
    if form.validate_on_submit():
        # Get form data
        email = form.email.data.lower().strip()
        password = form.password.data
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        admin_code = request.form.get('admin_code')  # Get admin code from form
        
        # Check if user already exists
        if User.email_exists(email, mongo):
            flash('Email already registered. Please use a different email or login.', 'error')
            return render_template('auth/admin_direct.html', form=form)
        
        # Verify admin invitation code
        if admin_code != 'ADMIN2025':  # Replace with actual verification logic
            flash('Invalid admin invitation code. Please check and try again.', 'error')
            return render_template('auth/admin_direct.html', form=form)
        
        # Store user data in session
        session['user_data'] = {
            'email': email,
            'password': password,
            'role': 'admin',
            'first_name': first_name,
            'last_name': last_name
        }
        
        return redirect(url_for('auth.admin_registration'))
    
    return render_template('auth/admin_direct.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))
