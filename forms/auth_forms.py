from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    """Login form."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ], render_kw={'placeholder': 'Enter your email'})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ], render_kw={'placeholder': 'Enter your password'})
    
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class SignupForm(FlaskForm):
    """Registration form."""
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required.'),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters.')
    ], render_kw={'placeholder': 'Enter your first name'})
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required.'),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters.')
    ], render_kw={'placeholder': 'Enter your last name'})
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ], render_kw={'placeholder': 'Enter your email'})
    
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('company', 'Company/Organization'),
        ('admin', 'Administrator')
    ], validators=[DataRequired(message='Please select your role.')])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ], render_kw={'placeholder': 'Create a password'})
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ], render_kw={'placeholder': 'Confirm your password'})
    
    submit = SubmitField('Create Account')
