"""
Dashboard Preview Script for InternGenius

This script creates a simple route that allows you to view all dashboards
without needing to be authenticated. Use this for development and preview only.
"""
from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'preview-key-for-development'

@app.route('/')
def index():
    return """
    <h1>Dashboard Previews</h1>
    <ul>
        <li><a href="/preview/student">Student Dashboard</a></li>
        <li><a href="/preview/company">Company Dashboard</a></li>
        <li><a href="/preview/admin">Admin Dashboard</a></li>
    </ul>
    """

@app.route('/preview/student')
def student_preview():
    class User:
        first_name = "John"
        role = "student"
    
    return render_template('dashboards/student_dashboard.html', user=User())

@app.route('/preview/company')
def company_preview():
    class User:
        def get_full_name(self):
            return "TechCorp Inc."
        role = "company"
    
    return render_template('dashboards/company_dashboard.html', user=User())

@app.route('/preview/admin')
def admin_preview():
    class User:
        first_name = "Admin"
        role = "admin"
    
    return render_template('dashboards/admin_dashboard.html', user=User())

if __name__ == '__main__':
    print("🌟 Starting Dashboard Preview Server...")
    print("📋 Available URLs:")
    print("   • Student Dashboard: http://127.0.0.1:5000/preview/student")
    print("   • Company Dashboard: http://127.0.0.1:5000/preview/company")
    print("   • Admin Dashboard: http://127.0.0.1:5000/preview/admin")
    print("\n🚀 Press Ctrl+C to stop the server\n")
    app.run(debug=True)
