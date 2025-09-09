from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Simple route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Routes that redirect to the index for demo purposes
@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('index.html')

@app.route('/direct_student_registration')
def direct_student_registration():
    return redirect(url_for('index'))

@app.route('/direct_company_registration')
def direct_company_registration():
    return redirect(url_for('index'))

@app.route('/direct_admin_registration')
def direct_admin_registration():
    return redirect(url_for('index'))

# Additional dummy routes to prevent 404 errors from the navbar/links
@app.route('/dashboard')
def dashboard():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
