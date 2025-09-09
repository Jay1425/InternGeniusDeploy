"""
User model for authentication and role management.
"""
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class User:
    def __init__(self, email, password_hash, role, first_name, last_name, is_active=True, created_at=None, last_login=None, _id=None):
        self._id = _id
        self.email = email
        self.password_hash = password_hash
        self.role = role  # 'student', 'company', or 'admin'
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login

    @classmethod
    def create_user(cls, email, password, role, first_name, last_name):
        """Create a new user with hashed password."""
        password_hash = generate_password_hash(password).decode('utf-8')
        return cls(
            email=email,
            password_hash=password_hash,
            role=role,
            first_name=first_name,
            last_name=last_name
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
        return f"{self.first_name} {self.last_name}"

    def check_password(self, password):
        """Check if provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login": self.last_login
        }

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
        """Get user by email."""
        user_data = mongo.db.users.find_one({"email": email})
        if user_data:
            return cls(
                _id=user_data['_id'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                role=user_data['role'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_active=user_data.get('is_active', True),
                created_at=user_data.get('created_at'),
                last_login=user_data.get('last_login')
            )
        return None

    @classmethod
    def get_by_id(cls, user_id, mongo):
        """Get user by ID."""
        try:
            user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return cls(
                    _id=user_data['_id'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    role=user_data['role'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=user_data.get('is_active', True),
                    created_at=user_data.get('created_at'),
                    last_login=user_data.get('last_login')
                )
        except:
            pass
        return None
