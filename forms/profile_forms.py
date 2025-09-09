from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, URL, Optional
from wtforms.fields import MultipleFileField

class StudentProfileForm(FlaskForm):
    """Student profile completion form."""
    # Academic Information
    institution = StringField('Institution/University', validators=[
        DataRequired(message='Institution name is required.'),
        Length(min=2, max=100, message='Institution name must be between 2 and 100 characters.')
    ], render_kw={'placeholder': 'Enter your college/university name'})
    
    degree = SelectField('Degree', choices=[
        ('', 'Select your degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('diploma', 'Diploma'),
        ('certificate', 'Certificate Program'),
        ('other', 'Other')
    ], validators=[DataRequired(message='Degree information is required.')])
    
    field_of_study = StringField('Field of Study', validators=[
        DataRequired(message='Field of study is required.'),
        Length(min=2, max=100, message='Field of study must be between 2 and 100 characters.')
    ], render_kw={'placeholder': 'E.g., Computer Science, Mechanical Engineering'})
    
    graduation_year = SelectField('Expected Graduation Year', validators=[
        DataRequired(message='Expected graduation year is required.')
    ], choices=[(str(year), str(year)) for year in range(2023, 2031)])
    
    # Contact and Personal Information
    phone = StringField('Phone Number', validators=[
        DataRequired(message='Phone number is required.'),
        Length(min=10, max=15, message='Please enter a valid phone number.')
    ], render_kw={'placeholder': 'Enter your contact number'})
    
    city = StringField('City', validators=[
        DataRequired(message='City is required.')
    ], render_kw={'placeholder': 'Enter your city'})
    
    state = StringField('State', validators=[
        DataRequired(message='State is required.')
    ], render_kw={'placeholder': 'Enter your state'})
    
    # Skills & Interests
    skills = StringField('Skills (Comma separated)', validators=[
        DataRequired(message='Please list at least one skill.')
    ], render_kw={'placeholder': 'E.g., Python, Java, Data Analysis, Project Management'})
    
    interests = StringField('Areas of Interest (Comma separated)', validators=[
        DataRequired(message='Please list at least one area of interest.')
    ], render_kw={'placeholder': 'E.g., Machine Learning, Web Development, IoT'})
    
    # Documents
    resume = FileField('Upload Resume (PDF format)', validators=[
        DataRequired(message='Resume is required.')
    ])
    
    # Bio
    bio = TextAreaField('Brief Bio', validators=[
        Optional(),
        Length(max=500, message='Bio should not exceed 500 characters.')
    ], render_kw={'placeholder': 'Tell us about yourself in a few sentences', 'rows': 4})
    
    # Social Media & Portfolio
    linkedin = StringField('LinkedIn Profile', validators=[
        Optional(),
        URL(message='Please enter a valid LinkedIn URL.')
    ], render_kw={'placeholder': 'https://linkedin.com/in/yourprofile'})
    
    github = StringField('GitHub Profile', validators=[
        Optional(),
        URL(message='Please enter a valid GitHub URL.')
    ], render_kw={'placeholder': 'https://github.com/yourusername'})
    
    portfolio = StringField('Portfolio Website', validators=[
        Optional(),
        URL(message='Please enter a valid URL.')
    ], render_kw={'placeholder': 'https://yourportfolio.com'})
    
    # Notifications
    notifications = BooleanField('Receive email notifications for new internship opportunities', default=True)
    
    submit = SubmitField('Complete Profile')


class CompanyProfileForm(FlaskForm):
    """Company/Organization profile completion form."""
    # Company Information
    company_name = StringField('Company/Organization Name', validators=[
        DataRequired(message='Company name is required.'),
        Length(min=2, max=100, message='Company name must be between 2 and 100 characters.')
    ], render_kw={'placeholder': 'Enter your company name'})
    
    industry = SelectField('Industry', choices=[
        ('', 'Select industry'),
        ('technology', 'Technology & IT'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance & Banking'),
        ('education', 'Education'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('media', 'Media & Entertainment'),
        ('nonprofit', 'Non-Profit'),
        ('government', 'Government'),
        ('consulting', 'Consulting'),
        ('energy', 'Energy'),
        ('telecom', 'Telecommunications'),
        ('automotive', 'Automotive'),
        ('other', 'Other')
    ], validators=[DataRequired(message='Industry is required.')])
    
    company_size = SelectField('Company Size', choices=[
        ('', 'Select company size'),
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1001-5000', '1001-5000 employees'),
        ('5000+', '5000+ employees')
    ], validators=[DataRequired(message='Company size is required.')])
    
    # Contact Information
    contact_person = StringField('Contact Person Name', validators=[
        DataRequired(message='Contact person name is required.')
    ], render_kw={'placeholder': 'Full name of the primary contact person'})
    
    contact_position = StringField('Position/Title', validators=[
        DataRequired(message='Position/title is required.')
    ], render_kw={'placeholder': 'E.g., HR Manager, Recruitment Lead'})
    
    contact_email = StringField('Contact Email', validators=[
        DataRequired(message='Contact email is required.'),
        Email(message='Please enter a valid email address.')
    ], render_kw={'placeholder': 'Email for internship inquiries'})
    
    phone = StringField('Phone Number', validators=[
        DataRequired(message='Phone number is required.'),
        Length(min=10, max=15, message='Please enter a valid phone number.')
    ], render_kw={'placeholder': 'Enter contact number'})
    
    # Location
    headquarters = StringField('Headquarters Location', validators=[
        DataRequired(message='Headquarters location is required.')
    ], render_kw={'placeholder': 'City, State, Country'})
    
    # Company Details
    website = StringField('Company Website', validators=[
        DataRequired(message='Company website is required.'),
        URL(message='Please enter a valid URL.')
    ], render_kw={'placeholder': 'https://www.yourcompany.com'})
    
    company_description = TextAreaField('Company Description', validators=[
        DataRequired(message='Company description is required.'),
        Length(min=100, max=1000, message='Description should be between 100 and 1000 characters.')
    ], render_kw={'placeholder': 'Describe your company, mission, and culture', 'rows': 5})
    
    # Company Logo and Verification
    logo = FileField('Company Logo (PNG/JPEG format)', validators=[
        DataRequired(message='Company logo is required.')
    ])
    
    registration_document = FileField('Company Registration Document (PDF format)', validators=[
        DataRequired(message='Company registration document is required for verification.')
    ])
    
    # Social Media
    linkedin = StringField('LinkedIn Company Page', validators=[
        Optional(),
        URL(message='Please enter a valid LinkedIn URL.')
    ], render_kw={'placeholder': 'https://linkedin.com/company/yourcompany'})
    
    # Terms
    terms = BooleanField('I confirm that I am authorized to represent this company and the information provided is accurate', validators=[
        DataRequired(message='You must confirm this to proceed.')
    ])
    
    submit = SubmitField('Complete Company Profile')


class AdminProfileForm(FlaskForm):
    """Administrator profile completion form."""
    # Admin Information
    admin_id = StringField('Admin ID', validators=[
        DataRequired(message='Admin ID is required.')
    ], render_kw={'placeholder': 'Enter your admin identification number'})
    
    department = SelectField('Department', choices=[
        ('', 'Select department'),
        ('platform_mgmt', 'Platform Management'),
        ('user_support', 'User Support'),
        ('content_moderation', 'Content Moderation'),
        ('technical', 'Technical Administration'),
        ('analytics', 'Analytics & Reporting')
    ], validators=[DataRequired(message='Department is required.')])
    
    # Contact Information
    phone = StringField('Phone Number', validators=[
        DataRequired(message='Phone number is required.'),
        Length(min=10, max=15, message='Please enter a valid phone number.')
    ], render_kw={'placeholder': 'Enter your contact number'})
    
    alternate_email = StringField('Alternate Email', validators=[
        Optional(),
        Email(message='Please enter a valid email address.')
    ], render_kw={'placeholder': 'Enter an alternate email for notifications'})
    
    # Security Information
    security_question = SelectField('Security Question', choices=[
        ('', 'Select a security question'),
        ('first_pet', 'What was the name of your first pet?'),
        ('mother_maiden', 'What is your mother\'s maiden name?'),
        ('birth_city', 'In which city were you born?'),
        ('first_school', 'What was the name of your first school?'),
        ('favorite_book', 'What is your favorite book?')
    ], validators=[DataRequired(message='Security question is required.')])
    
    security_answer = StringField('Answer', validators=[
        DataRequired(message='Security answer is required.')
    ], render_kw={'placeholder': 'Enter your answer'})
    
    # Verification
    admin_verification_document = FileField('Admin Authorization Document (PDF format)', validators=[
        DataRequired(message='Admin verification document is required.')
    ])
    
    # Permissions
    permissions = SelectField('Access Level', choices=[
        ('full_admin', 'Full Administrator (All Permissions)'),
        ('user_admin', 'User Administrator (User Management Only)'),
        ('content_admin', 'Content Administrator (Content Management Only)'),
        ('report_admin', 'Reports Administrator (Analytics Access Only)')
    ], validators=[DataRequired(message='Access level is required.')])
    
    # Acceptance
    terms = BooleanField('I agree to maintain the confidentiality of user data and adhere to privacy policies', validators=[
        DataRequired(message='You must agree to the terms to proceed.')
    ])
    
    submit = SubmitField('Complete Admin Profile')
