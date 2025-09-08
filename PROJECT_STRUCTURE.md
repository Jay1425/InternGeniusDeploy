# InternGenius - Professional Flask Project Structure 🎓

## 📁 Project Structure

```
InternGenius/
│
├── 📄 app.py                          # Flask application factory
├── 📄 config.py                       # Configuration settings
├── 📄 requirements.txt                # Python dependencies
├── 📄 run.py                          # Application runner script
├── 📄 .env.example                    # Environment variables template
├── 📄 .gitignore                      # Git ignore rules
├── 📄 README.md                       # Project documentation
│
├── 📁 models/                          # Database models
│   ├── 📄 __init__.py
│   └── 📄 user_model.py               # User authentication model
│
├── 📁 routes/                          # Flask Blueprints (API routes)
│   ├── 📄 __init__.py
│   ├── 📄 auth_routes.py              # Authentication routes
│   ├── 📄 student_routes.py           # Student dashboard routes
│   ├── 📄 company_routes.py           # Company dashboard routes
│   └── 📄 admin_routes.py             # Admin dashboard routes
│
├── 📁 forms/                           # WTForms form definitions
│   ├── 📄 __init__.py
│   └── 📄 auth_forms.py               # Login/Signup forms
│
├── 📁 templates/                       # Jinja2 HTML templates
│   ├── 📄 base.html                   # Base template with navigation
│   ├── 📄 index.html                  # Homepage
│   ├── 📁 auth/
│   │   ├── 📄 login.html              # Login page
│   │   └── 📄 signup.html             # Registration page
│   ├── 📁 dashboards/
│   │   ├── 📄 student_dashboard.html  # Student dashboard
│   │   ├── 📄 company_dashboard.html  # Company dashboard
│   │   └── 📄 admin_dashboard.html    # Admin dashboard
│   └── 📁 errors/
│       ├── 📄 404.html                # 404 error page
│       └── 📄 500.html                # 500 error page
│
├── 📁 static/                          # Static files (CSS, JS, images)
│   ├── 📁 css/
│   │   └── 📄 style.css               # Custom styles
│   ├── 📁 js/
│   │   └── 📄 main.js                 # Custom JavaScript
│   └── 📁 images/
│
├── 📁 ml_module/                       # 🤖 Machine Learning Module (Separate)
│   ├── 📄 __init__.py
│   ├── 📄 dropout_predictor.py        # Student dropout prediction
│   ├── 📄 recommendation_engine.py    # Internship recommendations
│   ├── 📄 risk_assessor.py           # Risk assessment algorithms
│   ├── 📄 data_processor.py          # Data preprocessing
│   ├── 📁 models/                     # Trained ML models
│   └── 📁 data/                       # Training datasets
│
└── 📁 tests/                          # Unit tests
    ├── 📄 __init__.py
    ├── 📄 test_auth.py
    ├── 📄 test_models.py
    └── 📄 test_ml.py
```

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
# Clone repository
git clone https://github.com/vishakha1221/InternGenius.git
cd InternGenius

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure Environment**
```bash
# Copy environment template
copy .env.example .env  # Windows
# cp .env.example .env    # Linux/Mac

# Edit .env file with your settings:
# - MongoDB connection string
# - Secret keys
# - Email configuration
```

### 3. **Setup MongoDB**
```bash
# Install MongoDB locally or use MongoDB Atlas
# Default connection: mongodb://localhost:27017/interngenius

# Collections created automatically:
# - users (authentication)
# - student_profiles
# - company_profiles  
# - internships
# - applications
```

### 4. **Run Application**
```bash
# Using the run script
python run.py

# Or directly with Flask
flask run

# Application will be available at: http://127.0.0.1:5000
```

## 👥 User Roles & Features

### **🎓 Student Dashboard**
- **Profile Management**: Update personal information, skills, interests
- **Internship Discovery**: Browse and search available opportunities
- **Application Tracking**: Monitor application status and responses
- **AI Recommendations**: Get personalized internship suggestions
- **Risk Assessment**: Academic performance monitoring (ML-powered)

### **🏢 Company Dashboard**  
- **Internship Posting**: Create and manage internship opportunities
- **Candidate Management**: Review applications and shortlist students
- **Analytics**: Track posting performance and candidate quality
- **Messaging**: Communicate with potential interns

### **🛡️ Admin Dashboard**
- **User Management**: Oversee all students and companies
- **System Analytics**: Platform usage and performance metrics
- **ML Model Management**: Monitor and retrain prediction models
- **Content Moderation**: Review and approve internship postings

## 🤖 Machine Learning Features

### **Dropout Prediction System**
```python
# Features analyzed:
- Attendance percentage
- Grade trends (improving/declining/stable)  
- Assessment scores and assignment completion
- Fee payment status and financial issues
- Academic history (backlogs, course changes)
- Behavioral patterns (library usage, participation)
```

### **Risk Assessment Categories**
- 🟢 **Low Risk**: Students performing well across all metrics
- 🟡 **Medium Risk**: Some concerning patterns detected
- 🔴 **High Risk**: Multiple risk factors, immediate intervention needed

### **Intelligent Recommendations**
- Profile-based internship matching
- Skill gap analysis and suggestions
- Career path recommendations
- Academic improvement strategies

## 📊 Database Schema

### **Users Collection**
```javascript
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "role": "student | company | admin",
  "first_name": "John",
  "last_name": "Doe", 
  "is_active": true,
  "created_at": ISODate,
  "last_login": ISODate
}
```

### **Student Profiles Collection**
```javascript
{
  "_id": ObjectId,
  "user_id": "user_object_id",
  "personal_info": {
    "phone": "+1234567890",
    "date_of_birth": ISODate,
    "address": {...}
  },
  "education": {
    "university": "Stanford University",
    "degree": "Computer Science",
    "year": 3,
    "cgpa": 8.5
  },
  "skills": ["Python", "JavaScript", "React"],
  "interests": ["Web Development", "AI/ML"],
  "experience": [...],
  "preferences": {
    "location": ["Remote", "San Francisco"],
    "duration": "3-6 months",
    "stipend_range": [1000, 2000]
  }
}
```

## 🛠️ Technology Stack

### **Backend**
- **Flask 2.3.3**: Web framework
- **PyMongo**: MongoDB integration
- **Flask-Login**: Authentication management
- **Flask-WTF**: Form handling and validation
- **Flask-Bcrypt**: Password hashing

### **Frontend**
- **Bootstrap 5.3**: UI framework
- **Jinja2**: Template engine  
- **Font Awesome**: Icons
- **Custom CSS/JS**: Enhanced user experience

### **Machine Learning**
- **Scikit-learn**: ML algorithms
- **Pandas/NumPy**: Data processing
- **Joblib**: Model serialization
- **Matplotlib/Seaborn**: Data visualization

### **Database**
- **MongoDB**: NoSQL database
- **Collections**: Users, Profiles, Internships, Applications

## 🔐 Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **Session Management**: Flask-Login for user sessions
- **Role-Based Access**: Decorators for route protection
- **CSRF Protection**: WTForms CSRF tokens
- **Input Validation**: Server-side validation for all forms

## 📈 Monitoring & Analytics

- **User Registration Trends**: Track student and company signups
- **Internship Success Rates**: Monitor application-to-hire ratios
- **ML Model Performance**: Accuracy metrics and retraining schedules
- **System Health**: Server performance and uptime monitoring

## 🚦 Getting Started (Step by Step)

1. **Clone and Setup**
   ```bash
   git clone https://github.com/vishakha1221/InternGenius.git
   cd InternGenius
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   copy .env.example .env
   # Edit .env with your MongoDB connection and secret keys
   ```

3. **Run Application**
   ```bash
   python run.py
   ```

4. **Access Application**
   - Open browser: `http://127.0.0.1:5000`
   - Register as Student, Company, or Admin
   - Explore role-specific dashboards

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`  
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

**Built with ❤️ for Educational Excellence**

*InternGenius - Connecting Students with Opportunities through Intelligent Matching*
