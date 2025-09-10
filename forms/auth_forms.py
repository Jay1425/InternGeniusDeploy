"""
Authentication forms for user registration and login.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from wtforms.widgets import TextArea
import re

def validate_password_strength(form, field):
    """Custom validator for password strength"""
    password = field.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character.')

def validate_name(form, field):
    """Custom validator for names"""
    name = field.data
    if not re.match(r'^[a-zA-Z\s\-\'\.]+$', name):
        raise ValidationError('Name can only contain letters, spaces, hyphens, apostrophes, and periods.')
    if len(name.strip()) < 2:
        raise ValidationError('Name must be at least 2 characters long.')

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message='Email address is required.'),
        Email(message='Please enter a valid email address.'),
        Length(max=120, message='Email address is too long.')
    ], render_kw={'placeholder': 'Enter your email address', 'autocomplete': 'email'})
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=1, message='Password cannot be empty.')
    ], render_kw={'placeholder': 'Enter your password', 'autocomplete': 'current-password'})
    remember_me = BooleanField('Remember Me for 30 days')
    submit = SubmitField('Sign In')

class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required.'),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters.'),
        validate_name
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required.'),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters.'),
        validate_name
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message='Email address is required.'),
        Email(message='Please enter a valid email address.'),
        Length(max=120, message='Email address is too long.')
    ])
    role = SelectField('Register As', choices=[
        ('student', 'Student'),
        ('company', 'Company/Organization'),
        ('admin', 'Administrator')
    ], validators=[DataRequired(message='Please select your role.')])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        validate_password_strength
    ], description='Must be at least 8 characters with uppercase, lowercase, number, and special character.')
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    terms = BooleanField('I agree to the Terms of Service and Privacy Policy', validators=[
        DataRequired(message='You must agree to the terms to continue.')
    ])
    submit = SubmitField('Create Account')

class StudentProfileForm(FlaskForm):
    # Personal Information
    phone = StringField('Phone Number', validators=[DataRequired()])
    date_of_birth = StringField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[DataRequired()])
    
    # Address Information
    address_line1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line2 = StringField('Address Line 2')
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    pincode = StringField('Pincode', validators=[DataRequired()])
    
    # Education Information
    university = StringField('University/College', validators=[DataRequired()])
    degree = StringField('Degree', validators=[DataRequired()])
    specialization = StringField('Specialization')
    graduation_year = StringField('Expected Graduation Year', validators=[DataRequired()])
    cgpa = StringField('CGPA/Percentage')
    
    # Skills and Interests
    technical_skills = StringField('Technical Skills (comma-separated)')
    soft_skills = StringField('Soft Skills (comma-separated)')
    languages = StringField('Languages Known (comma-separated)')
    interests = StringField('Areas of Interest (comma-separated)', validators=[DataRequired()])
    
    # Preferences
    preferred_location = StringField('Preferred Work Location')
    internship_duration = SelectField('Preferred Internship Duration', choices=[
        ('1-3 months', '1-3 months'),
        ('3-6 months', '3-6 months'),
        ('6-12 months', '6-12 months'),
        ('flexible', 'Flexible')
    ])
    expected_stipend = StringField('Expected Monthly Stipend (₹)')
    work_mode = SelectField('Preferred Work Mode', choices=[
        ('remote', 'Remote'),
        ('in-person', 'In-person'),
        ('hybrid', 'Hybrid'),
        ('flexible', 'Flexible')
    ])
    
    submit = SubmitField('Save Profile')

class CompanyProfileForm(FlaskForm):
    company_name = StringField('Company/Organization Name', validators=[DataRequired()])
    industry = SelectField('Industry', choices=[
        ('technology', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('government', 'Government'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    company_size = SelectField('Company Size', choices=[
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-1000', '201-1000 employees'),
        ('1000+', '1000+ employees')
    ])
    website = StringField('Website URL')
    description = StringField('Company Description', widget=TextArea())
    address = StringField('Company Address', validators=[DataRequired()])
    contact_person = StringField('Contact Person Name', validators=[DataRequired()])
    contact_email = StringField('Contact Email', validators=[DataRequired(), Email()])
    contact_phone = StringField('Contact Phone', validators=[DataRequired()])
    
    submit = SubmitField('Save Company Profile')
