from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User
from app import mongo
from forms.auth_forms import LoginForm, SignupForm

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

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = SignupForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        
        # Check if user already exists
        if User.email_exists(email, mongo):
            flash('Email already registered. Please use a different email or login.', 'error')
            return render_template('auth/signup.html', form=form)
        
        # Create new user
        user = User(
            email=email,
            password=form.password.data,
            role=form.role.data,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip()
        )
        
        # Save to database
        user.save(mongo)
        
        flash(f'Account created successfully! Welcome to InternGenius, {user.get_full_name()}!', 'success')
        
        # Log the user in automatically
        login_user(user)
        
        # Redirect to appropriate dashboard
        if user.role == 'student':
            return redirect(url_for('student.dashboard'))
        elif user.role == 'company':
            return redirect(url_for('company.dashboard'))
        elif user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
    
    return render_template('auth/signup.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))
