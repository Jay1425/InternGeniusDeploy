"""
Routes package for InternGenius

This package contains all Flask Blueprint route definitions.
"""

from .auth_routes import auth_bp
from .student_routes import student_bp
from .company_routes import company_bp
from .admin_routes import admin_bp

__all__ = ['auth_bp', 'student_bp', 'company_bp', 'admin_bp']
