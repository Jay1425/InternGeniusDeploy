"""
User model for authentication and role management.
"""
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class User:
    def __init__(self, email, password_hash, role, first_name, last_name, is_active=True, 
                 created_at=None, last_login=None, _id=None, **kwargs):
        # Core authentication fields
        self._id = _id
        self.email = email
        self.password_hash = password_hash
        self.role = role  # 'student', 'company', or 'admin'
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login

        # Profile completion tracking
        self.profile_completed = kwargs.get('profile_completed', False)
        self.is_verified = kwargs.get('is_verified', False)
        self.login_count = kwargs.get('login_count', 0)

        # Personal information
        self.middle_name = kwargs.get('middle_name', '')
        self.phone = kwargs.get('phone', '')
        self.date_of_birth = kwargs.get('date_of_birth')
        self.gender = kwargs.get('gender', '')
        self.category = kwargs.get('category', '')
        self.aadhaar_number = kwargs.get('aadhaar_number', '')
        self.nationality = kwargs.get('nationality', '')

        # Educational information (for students)
        self.current_education = kwargs.get('current_education', '')
        self.institution_name = kwargs.get('institution_name', '')
        self.field_of_study = kwargs.get('field_of_study', '')
        self.year_of_study = kwargs.get('year_of_study', '')
        self.cgpa = kwargs.get('cgpa')

        # Skills and preferences
        self.skills = kwargs.get('skills', [])
        self.soft_skills = kwargs.get('soft_skills', [])
        self.interests = kwargs.get('interests', [])
        self.languages = kwargs.get('languages', [])
        self.preferred_locations = kwargs.get('preferred_locations', [])
        self.expected_stipend = kwargs.get('expected_stipend', '')
        self.internship_duration = kwargs.get('internship_duration', '')
        self.work_mode = kwargs.get('work_mode', '')
        self.availability = kwargs.get('availability', '')

        # Additional profile fields
        self.bio = kwargs.get('bio', '')
        self.linkedin_url = kwargs.get('linkedin_url', '')
        self.github_url = kwargs.get('github_url', '')
        self.portfolio_url = kwargs.get('portfolio_url', '')
        self.resume_filename = kwargs.get('resume_filename')
        self.profile_photo_filename = kwargs.get('profile_photo_filename')
        self.documents = kwargs.get('documents', {})

        # Collections
        self.education = kwargs.get('education', [])
        self.address = kwargs.get('address', {})

        # Company-specific fields (when role is 'company')
        self.company_name = kwargs.get('company_name', '')
        self.company_size = kwargs.get('company_size', '')
        self.industry = kwargs.get('industry', '')
        self.website = kwargs.get('website', '')
        self.description = kwargs.get('description', '')

    @classmethod
    def create_user(cls, email, password, role, first_name, last_name, **kwargs):
        """Create a new user with hashed password and optional comprehensive data."""
        password_hash = generate_password_hash(password).decode('utf-8')
        return cls(
            email=email,
            password_hash=password_hash,
            role=role,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )
    
    @classmethod
    def create_comprehensive_student(cls, form_data):
        """Create a comprehensive student user from form data."""
        password_hash = generate_password_hash(form_data['password']).decode('utf-8')
        
        return cls(
            email=form_data['email'],
            password_hash=password_hash,
            role='student',
            first_name=form_data['first_name'],
            last_name=form_data['last_name'],
            middle_name=form_data.get('middle_name', ''),
            phone=form_data.get('phone', ''),
            date_of_birth=form_data.get('date_of_birth'),
            gender=form_data.get('gender', ''),
            category=form_data.get('category', ''),
            aadhaar_number=form_data.get('aadhaar_number', ''),
            nationality=form_data.get('nationality', ''),
            # New comprehensive fields
            education=form_data.get('education', []),
            address=form_data.get('address', {}),
            skills=form_data.get('skills', []),
            soft_skills=form_data.get('soft_skills', []),
            interests=form_data.get('interests', []),
            languages=form_data.get('languages', []),
            preferred_locations=form_data.get('preferred_locations', []),
            expected_stipend=form_data.get('expected_stipend', ''),
            internship_duration=form_data.get('internship_duration', ''),
            work_mode=form_data.get('work_mode', ''),
            availability=form_data.get('availability', ''),
            documents=form_data.get('documents', {}),
            profile_completed=True,
            is_verified=False,
            login_count=0
        )

    def get_id(self):
        """Required by Flask-Login."""
        return str(self._id)

    @property
    def is_authenticated(self):
        """Required by Flask-Login."""
        return True

    @property
    def is_anonymous(self):
        """Required by Flask-Login."""
        return False

    def get_full_name(self):
        """Get user's full name."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}".strip()
        return f"{self.first_name} {self.last_name}".strip()

    def check_password(self, password):
        """Check if provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage."""
        if self.role == 'student':
            total_fields = 12
            completed_fields = 0
            
            # Core fields
            if self.first_name: completed_fields += 1
            if self.last_name: completed_fields += 1
            if self.email: completed_fields += 1
            if self.phone: completed_fields += 1
            if self.date_of_birth: completed_fields += 1
            if self.gender: completed_fields += 1
            if self.category: completed_fields += 1
            if self.nationality: completed_fields += 1
            
            # Educational fields
            if self.current_education: completed_fields += 1
            if self.institution_name: completed_fields += 1
            if self.field_of_study: completed_fields += 1
            if self.skills: completed_fields += 1
            
            return (completed_fields / total_fields) * 100
        
        return 0.0
    
    def has_complete_profile(self):
        """Check if user has a complete profile."""
        return self.get_profile_completion_percentage() >= 90.0
    
    def get_display_name(self):
        """Get display name for UI."""
        return self.get_full_name() or self.email.split('@')[0]

    def to_dict(self):
        data = {
            # Core authentication fields
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login": self.last_login,
            
            # Profile tracking
            "profile_completed": self.profile_completed,
            "is_verified": self.is_verified,
            "login_count": self.login_count,
            
            # Personal information
            "middle_name": self.middle_name,
            "phone": self.phone,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "category": self.category,
            "aadhaar_number": self.aadhaar_number,
            "nationality": self.nationality,
            
            # Educational information
            "current_education": self.current_education,
            "institution_name": self.institution_name,
            "field_of_study": self.field_of_study,
            "year_of_study": self.year_of_study,
            "cgpa": self.cgpa,
            
            # Skills and preferences
            "skills": self.skills,
            "soft_skills": self.soft_skills,
            "interests": self.interests,
            "languages": self.languages,
            "preferred_locations": self.preferred_locations,
            "expected_stipend": self.expected_stipend,
            "internship_duration": self.internship_duration,
            "work_mode": self.work_mode,
            "availability": self.availability,
            
            # Additional profile fields
            "bio": self.bio,
            "linkedin_url": self.linkedin_url,
            "github_url": self.github_url,
            "portfolio_url": self.portfolio_url,
            "resume_filename": self.resume_filename,
            "profile_photo_filename": self.profile_photo_filename,
            "documents": self.documents,
            
            # Collections
            "education": self.education,
            "address": self.address
        }
        
        # Add company-specific fields for company users
        if self.role == 'company':
            data.update({
                "company_name": self.company_name,
                "company_size": self.company_size,
                "industry": self.industry,
                "website": self.website,
                "description": self.description
            })
        
        return data

    def save(self, mongo):
        """Save user to database."""
        user_data = self.to_dict()
        result = mongo.db.users.insert_one(user_data)
        self._id = result.inserted_id
        return result

    @classmethod
    def email_exists(cls, email, mongo):
        """Check if a user with the given email exists in the database."""
        user = mongo.db.users.find_one({"email": email})
        return user is not None

    @classmethod
    def get_by_email(cls, email, mongo):
        """Get user by email with comprehensive data."""
        user_data = mongo.db.users.find_one({"email": email})
        if user_data:
            # Remove _id from kwargs to avoid conflict
            kwargs = {k: v for k, v in user_data.items() if k not in ['_id', 'email', 'password_hash', 'role', 'first_name', 'last_name', 'is_active', 'created_at', 'last_login']}
            
            return cls(
                _id=user_data['_id'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                role=user_data['role'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_active=user_data.get('is_active', True),
                created_at=user_data.get('created_at'),
                last_login=user_data.get('last_login'),
                **kwargs
            )
        return None

    @classmethod
    def get_by_id(cls, user_id, mongo):
        """Get user by ID with comprehensive data."""
        try:
            user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                # Remove _id from kwargs to avoid conflict
                kwargs = {k: v for k, v in user_data.items() if k not in ['_id', 'email', 'password_hash', 'role', 'first_name', 'last_name', 'is_active', 'created_at', 'last_login']}
                
                return cls(
                    _id=user_data['_id'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    role=user_data['role'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=user_data.get('is_active', True),
                    created_at=user_data.get('created_at'),
                    last_login=user_data.get('last_login'),
                    **kwargs
                )
        except Exception as e:
            print(f"Error getting user by ID: {e}")
        return None
