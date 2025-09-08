from flask import Flask, render_template, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from config import config
import os

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app(config_name=None):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    from models.user_model import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id, mongo)
    
    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.student_routes import student_bp
    from routes.company_routes import company_bp
    from routes.admin_routes import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Home route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            # Redirect to appropriate dashboard based on role
            if current_user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif current_user.role == 'company':
                return redirect(url_for('company.dashboard'))
            elif current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
        
        return render_template('index.html')
    
    # Dashboard redirect route
    @app.route('/dashboard')
    def dashboard():
        if current_user.is_authenticated:
            if current_user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif current_user.role == 'company':
                return redirect(url_for('company.dashboard'))
            elif current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
        
        return redirect(url_for('auth.login'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
