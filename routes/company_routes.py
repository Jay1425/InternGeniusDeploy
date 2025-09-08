from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

company_bp = Blueprint('company', __name__)

def company_required(f):
    """Decorator to require company role."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'company':
            flash('Access denied. Company privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@company_bp.route('/dashboard')
@login_required
@company_required
def dashboard():
    """Company dashboard."""
    return render_template('dashboards/company_dashboard.html', user=current_user)

@company_bp.route('/post-internship')
@login_required
@company_required
def post_internship():
    """Post a new internship."""
    return render_template('company/post_internship.html', user=current_user)

@company_bp.route('/manage-internships')
@login_required
@company_required
def manage_internships():
    """Manage company's posted internships."""
    return render_template('company/manage_internships.html', user=current_user)
