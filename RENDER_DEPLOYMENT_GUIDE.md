# 🚀 Render Deployment Guide for CLM Backend

## Overview
Complete guide to deploy CLM Backend on Render.

---

## ✅ Build & Start Commands

### Build Command
```bash
pip install -r requirements.txt && python manage.py migrate
```

**What it does:**
1. Installs all Python dependencies from requirements.txt
2. Runs Django migrations to set up the database schema

### Start Command
```bash
gunicorn clm_backend.wsgi
```

**What it does:**
- Starts the Django application using Gunicorn WSGI server
- Automatically handles request routing

---

## 🔧 Configuration Files

### 1. **Procfile** (Required)
Tells Render how to start the application.

```
web: gunicorn clm_backend.wsgi --log-file -
```

- `web:` - Process type
- `gunicorn clm_backend.wsgi` - Command to run
- `--log-file -` - Write logs to stdout

---

### 2. **runtime.txt** (Recommended)
Specifies Python version to avoid compatibility issues.

```
python-3.11.7
```

---

### 3. **render.yaml** (Optional - Advanced)
Complete service configuration for Render.

```yaml
services:
  - type: web
    name: clm-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt && python manage.py migrate
    startCommand: gunicorn clm_backend.wsgi
    healthCheckPath: /health/
    scaling:
      minInstances: 1
      maxInstances: 1
```

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare Repository
Ensure these files are in your repository root:
- ✅ `Procfile` - Start command
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Dependencies
- ✅ `.env.example` - Environment variables template (don't commit .env)

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### Step 3: Create New Web Service
1. Dashboard → **New +** → **Web Service**
2. Connect GitHub repository
3. Configure settings:

**Name:** `clm-backend` (or your preferred name)

**Environment:** `Python 3`

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py migrate
```

**Start Command:**
```bash
gunicorn clm_backend.wsgi
```

### Step 4: Environment Variables
Add these to Render dashboard (Settings → Environment):

```
# Django Settings
DEBUG=false
ALLOWED_HOSTS=your-app-name.onrender.com
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=clm_backend.settings

# Database (Render provides DATABASE_URL automatically)
DATABASE_URL=postgres://user:password@host:5432/database

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=suhaib96886@gmail.com
EMAIL_HOST_PASSWORD=ruuo ntzn djvu hddg
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=suhaib96886@gmail.com

# Notification Settings
NOTIFICATIONS_ENABLED=True
APPROVAL_EMAIL_ENABLED=True
APPROVAL_IN_APP_ENABLED=True

# AWS (if using R2/S3)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket

# App Configuration
APP_URL=https://your-app-name.onrender.com
APP_NAME=Contract Lifecycle Management System
```

### Step 5: Database Setup
1. Click **Create Database** in Render dashboard
2. Choose PostgreSQL (recommended for Django)
3. Render will automatically set `DATABASE_URL`
4. Migrations run automatically with build command

### Step 6: Deploy
1. Click **Deploy**
2. Render will:
   - Clone your repository
   - Install requirements.txt
   - Run migrations
   - Start Gunicorn server
3. Monitor logs in Render dashboard

---

## 🔍 Verification Checklist

### After Deployment
- [ ] Application is running (check status in Render dashboard)
- [ ] Health check passes (`GET /health/`)
- [ ] Can access API endpoints
- [ ] Database migrations completed
- [ ] Email notifications working
- [ ] Static files serving correctly
- [ ] No error logs in Render logs

### Test Endpoints
```bash
# Health check
curl https://your-app-name.onrender.com/health/

# Auth login
curl -X POST https://your-app-name.onrender.com/api/auth/login/

# List contracts
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-app-name.onrender.com/api/contracts/
```

---

## ⚙️ Advanced Configuration

### Enable HTTPS
- Render automatically provides free SSL certificate
- Enable auto-redirect: Settings → HTTP to HTTPS

### Custom Domain
1. Add domain in Render dashboard
2. Update DNS records
3. CNAME: `your-app-name.onrender.com`

### Scaling
```yaml
# In render.yaml
scaling:
  minInstances: 1      # Minimum running instances
  maxInstances: 3      # Maximum for auto-scaling
```

### Background Jobs (Optional)
For Celery tasks:
```yaml
services:
  - type: background
    name: celery-worker
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A clm_backend worker -l info
```

---

## 🐛 Troubleshooting

### Build Fails
**Error:** `pip: command not found`
- **Fix:** Ensure Python 3.11.7 specified in runtime.txt

**Error:** `psycopg2 compilation fails`
- **Fix:** Already using psycopg2-binary in requirements.txt (compatible with Render)

### Database Connection Issues
**Error:** `FATAL: role "postgres" does not exist`
- **Fix:** Run migrations manually in Render Shell:
  ```bash
  python manage.py migrate
  ```

### Email Not Sending
**Error:** `SMTPAuthenticationError`
- **Fix:** Verify EMAIL_HOST_PASSWORD in environment variables (use app password, not Gmail password)

### Static Files Not Loading
**Error:** 404 on /static/
- **Fix:** Ensure STATIC_ROOT is set in settings.py:
  ```python
  STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
  ```

### Health Check Fails
**Error:** `health/ returns 404`
- **Fix:** Ensure health endpoint exists in views, or update healthCheckPath in render.yaml

---

## 📊 Monitoring

### View Logs
1. Render Dashboard → Your Service → Logs
2. Real-time application logs
3. Filter by severity level

### Performance Metrics
- **CPU Usage:** Monitor in Render dashboard
- **Memory:** Alert if exceeding limits
- **Response Times:** Check API latency

### Error Tracking (Optional)
Add Sentry for error monitoring:
```python
# In settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

---

## 💡 Best Practices

1. **Environment Variables**
   - Never commit `.env` file
   - Use `.env.example` for template
   - Rotate secrets regularly

2. **Database**
   - Backup database before deployments
   - Monitor disk usage
   - Test migrations locally first

3. **Performance**
   - Use caching (Redis)
   - Optimize database queries
   - Use CDN for static files

4. **Security**
   - Set `DEBUG=False` in production
   - Use strong SECRET_KEY
   - Enable HTTPS (automatic on Render)
   - Keep dependencies updated

5. **Monitoring**
   - Check logs regularly
   - Set up alerts for errors
   - Monitor email sending
   - Track approval workflow metrics

---

## 📞 Support

**Render Documentation:** https://render.com/docs

**Common Issues:**
- Database setup: https://render.com/docs/databases
- Environment variables: https://render.com/docs/environment-variables
- Troubleshooting: https://render.com/docs/troubleshooting

---

## ✨ Quick Reference

| Command | Purpose |
|---------|---------|
| `pip install -r requirements.txt` | Install dependencies |
| `python manage.py migrate` | Run database migrations |
| `gunicorn clm_backend.wsgi` | Start production server |
| `python manage.py collectstatic` | Collect static files |
| `python manage.py shell` | Django interactive shell |
| `python manage.py createsuperuser` | Create admin user |

---

**Status:** Ready for Render deployment ✅
