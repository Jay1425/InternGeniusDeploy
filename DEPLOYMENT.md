# 🚀 InternGenius Deployment Guide

## 📋 Pre-Deployment Checklist

### **1. Environment Preparation**
- [ ] Python 3.8+ installed
- [ ] MongoDB setup (local or Atlas)
- [ ] Domain name configured (production)
- [ ] SSL certificate ready (production)
- [ ] Server/hosting platform selected

### **2. Security Configuration**
- [ ] Strong secret keys generated
- [ ] Environment variables secured
- [ ] Database credentials protected
- [ ] HTTPS enabled (production)
- [ ] CSRF protection verified

---

## 🖥️ Local Development Deployment

### **Quick Start**
```bash
# 1. Clone and setup
git clone https://github.com/vishakha1221/InternGenius.git
cd InternGenius
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configure environment
copy .env.example .env
# Edit .env with your settings

# 3. Start MongoDB (if local)
mongod --dbpath=data/db

# 4. Run application
python run.py
```

### **Access Points**
- **Application**: http://127.0.0.1:5000
- **Student Dashboard**: http://127.0.0.1:5000/student/dashboard
- **Company Dashboard**: http://127.0.0.1:5000/company/dashboard
- **Admin Dashboard**: http://127.0.0.1:5000/admin/dashboard

---

## ☁️ Production Deployment Options

### **Option 1: Heroku Deployment**

#### **1. Heroku Setup**
```bash
# Install Heroku CLI
# Create Heroku app
heroku create interngenius-app
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-production-secret-key
```

#### **2. MongoDB Atlas Configuration**
```bash
# Set MongoDB Atlas connection
heroku config:set MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/interngenius
```

#### **3. Deploy to Heroku**
```bash
# Create Procfile
echo "web: gunicorn run:app" > Procfile

# Deploy
git add .
git commit -m "Production deployment"
git push heroku main
```

#### **4. Heroku Configuration Files**

**Procfile:**
```
web: gunicorn run:app --bind 0.0.0.0:$PORT
```

**runtime.txt:**
```
python-3.11.0
```

---

### **Option 2: DigitalOcean Droplet**

#### **1. Server Setup**
```bash
# Create Ubuntu 20.04 droplet
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv nginx -y
```

#### **2. Application Deployment**
```bash
# Clone application
git clone https://github.com/vishakha1221/InternGenius.git
cd InternGenius

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### **3. Gunicorn Configuration**
```bash
# Create gunicorn service
sudo nano /etc/systemd/system/interngenius.service
```

**Service File Content:**
```ini
[Unit]
Description=InternGenius Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/ubuntu/InternGenius
Environment="PATH=/home/ubuntu/InternGenius/venv/bin"
ExecStart=/home/ubuntu/InternGenius/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### **4. Nginx Configuration**
```nginx
# /etc/nginx/sites-available/interngenius
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /home/ubuntu/InternGenius/static;
        expires 30d;
    }
}
```

#### **5. Enable Services**
```bash
# Enable and start services
sudo systemctl enable interngenius
sudo systemctl start interngenius
sudo systemctl enable nginx
sudo systemctl start nginx

# Enable site
sudo ln -s /etc/nginx/sites-available/interngenius /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl reload nginx
```

---

### **Option 3: AWS EC2 Deployment**

#### **1. EC2 Instance Setup**
- Launch Ubuntu 20.04 LTS instance
- Configure Security Groups (ports 22, 80, 443)
- Attach Elastic IP (optional)

#### **2. Application Setup**
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx git -y

# Clone and setup application
git clone https://github.com/vishakha1221/InternGenius.git
cd InternGenius
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### **3. MongoDB Atlas Integration**
```bash
# Configure MongoDB Atlas connection
export MONGO_URI="mongodb+srv://user:password@cluster.mongodb.net/interngenius"
# Add to .env file permanently
```

---

## 🛠️ Production Environment Variables

### **Required Settings**
```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=super-secure-production-key-here
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/interngenius
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

### **Security Hardening**
```bash
# Additional security headers
FORCE_HTTPS=True
SESSION_COOKIE_SAMESITE=Strict
CSRF_COOKIE_SECURE=True
BCRYPT_LOG_ROUNDS=14
```

---

## 📊 Monitoring & Maintenance

### **Health Checks**
```python
# Add to app.py
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow()}
```

### **Log Monitoring**
```bash
# Monitor application logs
sudo journalctl -u interngenius -f

# Monitor nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### **Database Backup**
```bash
# MongoDB backup (if self-hosted)
mongodump --db interngenius --out backup/

# MongoDB Atlas automatic backups available
```

---

## 🔒 SSL/HTTPS Setup

### **Let's Encrypt (Free SSL)**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 🚀 Performance Optimization

### **1. Application Optimization**
- Enable gzip compression
- Implement caching (Redis)
- Optimize database queries
- Use CDN for static files

### **2. Server Optimization**
```bash
# Increase worker processes
# Update gunicorn configuration
--workers $((2 * $(nproc) + 1))
--worker-class gevent
--worker-connections 1000
```

### **3. Database Optimization**
- Index frequently queried fields
- Monitor query performance
- Regular maintenance tasks

---

## 🔧 Troubleshooting

### **Common Issues**
1. **Port already in use**: `sudo lsof -i :5000`
2. **Permission denied**: Check file ownership and permissions
3. **Database connection**: Verify MongoDB URI and network access
4. **Static files not loading**: Check nginx configuration

### **Debug Commands**
```bash
# Check service status
sudo systemctl status interngenius

# View application logs
sudo journalctl -u interngenius --since "1 hour ago"

# Test configuration
nginx -t
gunicorn --check-config run:app
```

---

## 📞 Support & Maintenance

### **Regular Tasks**
- [ ] Monitor application logs
- [ ] Update dependencies monthly
- [ ] Database backup verification
- [ ] SSL certificate renewal
- [ ] Security patches

### **Performance Monitoring**
- Server resource usage
- Response times
- Database performance
- User activity metrics

---

*Last Updated: December 2024*
*For support, contact: admin@interngenius.com*
