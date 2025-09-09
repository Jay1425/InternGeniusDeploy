from flask import Flask, render_template, redirect, url_for, request, flash, session
import os
import secrets
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure random key
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Enable CSRF protection
csrf = CSRFProtect(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)

# Simple route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('index.html')

# Student registration routes
@app.route('/direct_student_registration')
def direct_student_registration():
    return render_template('student_registration.html')

@app.route('/student_profile')
def student_profile():
    # Check if student data exists in session
    if 'registration_data' not in session:
        flash('Profile data not found. Please register first.', 'warning')
        return redirect(url_for('direct_student_registration'))
    
    # Get student data from session
    student = session['registration_data']
    
    return render_template('student_profile.html', student=student)

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
            resume_file = files['resume']
            resume_filename = secure_filename(resume_file.filename)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', resume_filename)
            resume_file.save(resume_path)
            form_data['resume_filename'] = resume_filename
        
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
        
        # Store the complete profile in session
        session['registration_data'] = profile
        
        # Flash success message
        flash('Registration successful! Welcome to InternGenius', 'success')
        
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

# Company registration route (placeholder)
@app.route('/direct_company_registration')
def direct_company_registration():
    return redirect(url_for('index'))

# Admin registration route (placeholder)
@app.route('/direct_admin_registration')
def direct_admin_registration():
    return redirect(url_for('index'))

# Dashboard routes (placeholder)
@app.route('/dashboard')
def dashboard():
    return redirect(url_for('index'))

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
