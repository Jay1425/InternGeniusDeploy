# 📡 InternGenius API Documentation

## 🔐 Authentication Endpoints

### **POST /auth/login**
User login authentication

**Request Body:**
```json
{
    "email": "student@example.com",
    "password": "password123"
}
```

**Response (Success):**
```json
{
    "status": "success",
    "message": "Login successful",
    "user": {
        "id": "user_id",
        "email": "student@example.com",
        "role": "Student",
        "name": "John Doe"
    },
    "redirect_url": "/student/dashboard"
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "Invalid email or password"
}
```

---

### **POST /auth/signup**
User registration

**Request Body:**
```json
{
    "full_name": "John Doe",
    "email": "student@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "role": "Student"
}
```

**Response (Success):**
```json
{
    "status": "success",
    "message": "Account created successfully",
    "user_id": "new_user_id"
}
```

---

### **POST /auth/logout**
User logout

**Response:**
```json
{
    "status": "success",
    "message": "Logged out successfully"
}
```

---

## 🎓 Student Endpoints

### **GET /student/dashboard**
Student dashboard data

**Headers:**
```
Authorization: Bearer <session_token>
Content-Type: application/json
```

**Response:**
```json
{
    "user": {
        "name": "John Doe",
        "email": "john@example.com",
        "profile_completion": 75
    },
    "stats": {
        "applications_sent": 12,
        "interviews_scheduled": 3,
        "saved_internships": 8,
        "profile_views": 45
    },
    "recent_activities": [
        {
            "type": "application",
            "title": "Applied to Software Developer Intern",
            "company": "Tech Corp",
            "timestamp": "2024-12-15T10:30:00Z"
        }
    ],
    "recommendations": [
        {
            "id": "internship_id",
            "title": "Python Developer Intern",
            "company": "StartupXYZ",
            "match_score": 92
        }
    ]
}
```

---

### **GET /student/profile**
Get student profile

**Response:**
```json
{
    "personal_info": {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "location": "New York, NY"
    },
    "education": {
        "degree": "Bachelor of Technology",
        "field_of_study": "Computer Science",
        "institution": "ABC University",
        "graduation_year": 2025,
        "gpa": 3.8
    },
    "skills": [
        "Python", "JavaScript", "React", "MongoDB"
    ],
    "experience": [
        {
            "title": "Software Development Intern",
            "company": "TechStart",
            "duration": "Summer 2023",
            "description": "Developed web applications using React and Node.js"
        }
    ]
}
```

---

### **PUT /student/profile**
Update student profile

**Request Body:**
```json
{
    "personal_info": {
        "phone": "+1234567890",
        "location": "Boston, MA"
    },
    "skills": ["Python", "JavaScript", "React", "MongoDB", "Docker"],
    "bio": "Passionate computer science student with experience in full-stack development"
}
```

---

### **GET /student/internships**
Browse available internships

**Query Parameters:**
- `search`: Search term (optional)
- `location`: Filter by location (optional)
- `company`: Filter by company (optional)
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20)

**Response:**
```json
{
    "internships": [
        {
            "id": "internship_id",
            "title": "Software Developer Intern",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "type": "Remote",
            "duration": "3 months",
            "stipend": "$2000/month",
            "description": "Join our development team...",
            "requirements": ["Python", "Git", "Problem Solving"],
            "posted_date": "2024-12-10T00:00:00Z",
            "application_deadline": "2025-01-15T23:59:59Z"
        }
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 5,
        "total_results": 87
    }
}
```

---

### **POST /student/applications**
Apply for internship

**Request Body:**
```json
{
    "internship_id": "internship_id",
    "cover_letter": "I am very interested in this position...",
    "additional_info": "Available to start immediately"
}
```

---

## 🏢 Company Endpoints

### **GET /company/dashboard**
Company dashboard data

**Response:**
```json
{
    "company": {
        "name": "Tech Corp",
        "industry": "Technology",
        "location": "San Francisco, CA"
    },
    "stats": {
        "active_postings": 5,
        "total_applications": 156,
        "interviews_scheduled": 12,
        "interns_hired": 3
    },
    "recent_applications": [
        {
            "applicant_name": "John Doe",
            "position": "Software Developer Intern",
            "application_date": "2024-12-15T10:30:00Z",
            "status": "Under Review"
        }
    ]
}
```

---

### **POST /company/internships**
Create new internship posting

**Request Body:**
```json
{
    "title": "Software Developer Intern",
    "description": "Join our development team to work on exciting projects...",
    "requirements": ["Python", "Git", "Problem Solving"],
    "location": "San Francisco, CA",
    "type": "Hybrid",
    "duration": "3 months",
    "stipend": "$2000/month",
    "application_deadline": "2025-01-15T23:59:59Z",
    "positions_available": 2
}
```

---

### **GET /company/applications**
View applications for company postings

**Query Parameters:**
- `internship_id`: Filter by specific internship (optional)
- `status`: Filter by application status (optional)
- `page`: Page number (default: 1)

**Response:**
```json
{
    "applications": [
        {
            "id": "application_id",
            "applicant": {
                "name": "John Doe",
                "email": "john@example.com",
                "university": "ABC University"
            },
            "internship": {
                "title": "Software Developer Intern",
                "id": "internship_id"
            },
            "status": "Under Review",
            "applied_date": "2024-12-15T10:30:00Z",
            "cover_letter": "I am very interested...",
            "resume_url": "/uploads/resumes/john_doe_resume.pdf"
        }
    ]
}
```

---

### **PUT /company/applications/{application_id}/status**
Update application status

**Request Body:**
```json
{
    "status": "Interview Scheduled",
    "notes": "Candidate looks promising. Schedule technical interview."
}
```

---

## 🛡️ Admin Endpoints

### **GET /admin/dashboard**
Admin dashboard overview

**Response:**
```json
{
    "system_stats": {
        "total_users": 1250,
        "active_students": 987,
        "active_companies": 156,
        "total_internships": 342,
        "successful_placements": 89
    },
    "recent_registrations": [
        {
            "name": "New User",
            "email": "user@example.com",
            "role": "Student",
            "registration_date": "2024-12-15T09:00:00Z"
        }
    ],
    "ml_predictions": {
        "high_risk_students": 23,
        "prediction_accuracy": 87.5,
        "last_model_update": "2024-12-10T12:00:00Z"
    }
}
```

---

### **GET /admin/users**
Manage users

**Query Parameters:**
- `role`: Filter by user role (Student/Company/Admin)
- `status`: Filter by account status (Active/Inactive/Suspended)
- `search`: Search by name or email
- `page`: Page number

**Response:**
```json
{
    "users": [
        {
            "id": "user_id",
            "name": "John Doe",
            "email": "john@example.com",
            "role": "Student",
            "status": "Active",
            "registration_date": "2024-11-15T10:00:00Z",
            "last_login": "2024-12-15T08:30:00Z"
        }
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 25,
        "total_users": 1250
    }
}
```

---

### **PUT /admin/users/{user_id}/status**
Update user status

**Request Body:**
```json
{
    "status": "Suspended",
    "reason": "Policy violation"
}
```

---

## 🤖 Machine Learning Endpoints

### **POST /api/ml/predict-dropout**
Predict student dropout risk

**Request Body:**
```json
{
    "student_id": "student_id",
    "academic_data": {
        "attendance_percentage": 75,
        "current_gpa": 3.2,
        "previous_gpa": 3.5,
        "assignments_completed": 85,
        "assessments_passed": 90,
        "fee_payment_status": "Paid",
        "backlogs": 1,
        "course_changes": 0,
        "library_visits": 45,
        "participation_score": 80
    }
}
```

**Response:**
```json
{
    "student_id": "student_id",
    "risk_level": "Medium",
    "risk_score": 0.65,
    "risk_factors": [
        "Declining GPA trend",
        "Below average attendance"
    ],
    "recommendations": [
        "Schedule academic counseling session",
        "Provide additional learning resources",
        "Monitor attendance closely"
    ],
    "prediction_confidence": 0.87,
    "generated_at": "2024-12-15T12:00:00Z"
}
```

---

### **GET /api/ml/recommendations/{student_id}**
Get personalized internship recommendations

**Response:**
```json
{
    "recommendations": [
        {
            "internship_id": "internship_id",
            "title": "Python Developer Intern",
            "company": "StartupXYZ",
            "match_score": 92,
            "matching_skills": ["Python", "Git", "Problem Solving"],
            "skill_gaps": ["Docker", "AWS"],
            "reasons": [
                "Strong match for required skills",
                "Company culture aligns with interests",
                "Location preference match"
            ]
        }
    ],
    "total_recommendations": 8,
    "last_updated": "2024-12-15T10:00:00Z"
}
```

---

## 📊 Analytics Endpoints

### **GET /api/analytics/dashboard**
General platform analytics

**Response:**
```json
{
    "user_metrics": {
        "new_registrations_this_month": 145,
        "active_users_this_week": 890,
        "user_retention_rate": 78.5
    },
    "internship_metrics": {
        "new_postings_this_month": 67,
        "application_rate": 4.2,
        "success_rate": 26.8
    },
    "engagement_metrics": {
        "avg_session_duration": "25 minutes",
        "page_views_per_session": 8.3,
        "bounce_rate": 23.4
    }
}
```

---

## 🔍 Search Endpoints

### **GET /api/search/internships**
Advanced internship search

**Query Parameters:**
- `q`: Search query
- `skills[]`: Array of required skills
- `location`: Location filter
- `company_size`: Company size preference
- `duration`: Internship duration
- `stipend_min`: Minimum stipend
- `stipend_max`: Maximum stipend
- `type`: Remote/Hybrid/On-site

---

### **GET /api/search/students**
Search students (Company access)

**Query Parameters:**
- `skills[]`: Array of required skills
- `education_level`: Education level filter
- `graduation_year`: Graduation year
- `location`: Location preference
- `availability`: Availability status

---

## 🔔 Notification Endpoints

### **GET /api/notifications**
Get user notifications

**Response:**
```json
{
    "notifications": [
        {
            "id": "notification_id",
            "type": "application_update",
            "title": "Application Status Updated",
            "message": "Your application for Software Developer Intern has been reviewed",
            "is_read": false,
            "created_at": "2024-12-15T11:30:00Z",
            "action_url": "/student/applications/application_id"
        }
    ],
    "unread_count": 3
}
```

---

### **PUT /api/notifications/{notification_id}/read**
Mark notification as read

**Response:**
```json
{
    "status": "success",
    "message": "Notification marked as read"
}
```

---

## 📋 Error Responses

### **Standard Error Format**
```json
{
    "status": "error",
    "error_code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
        "field": "email",
        "issue": "Invalid email format"
    },
    "timestamp": "2024-12-15T12:00:00Z"
}
```

### **Common Error Codes**
- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_REQUIRED`: User not authenticated
- `AUTHORIZATION_DENIED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_SERVER_ERROR`: Server-side error

---

## 🔒 Authentication

### **Session-Based Authentication**
- Login returns session cookie
- Include session cookie in subsequent requests
- Session expires after 1 hour of inactivity

### **Rate Limiting**
- 100 requests per hour per user
- 1000 requests per hour for companies
- Unlimited for admins

---

## 📝 Request/Response Headers

### **Required Headers**
```
Content-Type: application/json
User-Agent: InternGenius-Client/1.0
```

### **Response Headers**
```
Content-Type: application/json
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-API-Version: 1.0
```

---

*API Documentation v1.0 - Last Updated: December 2024*
