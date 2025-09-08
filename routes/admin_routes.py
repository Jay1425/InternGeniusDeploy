from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin role."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard."""
    return render_template('dashboards/admin_dashboard.html', user=current_user)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage all users."""
    return render_template('admin/manage_users.html', user=current_user)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Platform analytics and insights."""
    return render_template('admin/analytics.html', user=current_user)
