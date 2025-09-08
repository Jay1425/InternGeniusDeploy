from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

student_bp = Blueprint('student', __name__)

def student_required(f):
    """Decorator to require student role."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied. Student privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard."""
    return render_template('dashboards/student_dashboard.html', user=current_user)

@student_bp.route('/profile')
@login_required
@student_required
def profile():
    """Student profile page."""
    return render_template('student/profile.html', user=current_user)

@student_bp.route('/internships')
@login_required
@student_required
def internships():
    """Available internships for students."""
    return render_template('student/internships.html', user=current_user)
