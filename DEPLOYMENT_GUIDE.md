# 🚀 CLM Backend Deployment Guide

## Overview

This guide provides comprehensive build and deployment instructions for the CLM (Contract Lifecycle Management) backend application.

## 🆕 Recent Fixes Applied (Latest Update - January 2026)

### Pillow Compatibility Issue (UPDATED - FIXED)
- **Problem**: Pillow 10.2.0 failed to build on Render.com with Python 3.13, causing "KeyError: '__version__'" error
- **Root Cause**: Pillow 10.2.0 does NOT support Python 3.13 (despite documentation claims)
- **Solution**: Updated to Pillow>=10.3.0 which properly supports Python 3.13+
- **Files Updated**: `requirements.txt`, `render.yaml`, `build.sh`
- **Impact**: Resolves deployment failures on Render.com and other platforms using Python 3.13

### Build Process Improvements
- Enhanced build scripts with better dependency management
- Added explicit Python version specification (3.10.13)
- Improved error handling and logging
- Added `--no-cache-dir` flag for reliable package installation
- Removed forced Pillow version pinning that was causing conflicts

### Render.com Deployment Support
- Added `render.yaml` configuration file
- Optimized Gunicorn settings for production
- Automatic PostgreSQL database provisioning
- Environment variable templates for all required settings

## 📋 Prerequisites

### System Requirements
- Python 3.10.13
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional)

### Tools Required
- `pip` for Python package management
- `git` for version control
- `make` for build automation (optional)

## 🏗️ Build Commands

### Quick Build (Development)
```bash
# Make scripts executable
chmod +x build.sh deploy.sh

# Build for development
./build.sh development
```

### Production Build
```bash
# Build for production
./build.sh production
```

### Manual Build Steps
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run code quality checks (development only)
black . --exclude="venv/|__pycache__/|\.git/|migrations/"
isort . --skip="venv" --skip="__pycache__" --skip=".git" --skip="migrations"
flake8 . --exclude="venv,__pycache__,.git,migrations" --max-line-length=88

# 4. Run tests
python manage.py test --verbosity=2

# 5. Setup database
python manage.py migrate
python manage.py collectstatic --noinput --clear

# 6. Create superuser (optional)
python manage.py createsuperuser
```

## 🚀 Deployment Options

### Option 1: Heroku Deployment (Recommended for Quick Start)

#### Prerequisites
```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# Or download from https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login
```

#### Deploy to Heroku
```bash
# Deploy to production
./deploy.sh production heroku

# Or manually:
# 1. Create Heroku app
heroku create clm-backend-production

# 2. Set environment variables
heroku config:set DJANGO_SETTINGS_MODULE=clm_backend.settings
heroku config:set DEBUG=False
heroku config:set SECRET_KEY="$(openssl rand -base64 32)"

# 3. Add addons
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev

# 4. Deploy
git push heroku main

# 5. Run migrations
heroku run python manage.py migrate

# 6. Create superuser
heroku run python manage.py createsuperuser
```

#### Heroku Environment Variables
Set these in Heroku dashboard or via CLI:
```bash
# Django settings
DJANGO_SETTINGS_MODULE=clm_backend.settings
DEBUG=False
SECRET_KEY=your-secret-key-here

# Database (auto-set by Heroku Postgres addon)
DATABASE_URL=postgres://...

# Redis (auto-set by Heroku Redis addon)
REDIS_URL=r1.5: Render.com Deployment (Fixed - Recommended for Cloud)

#### Prerequisites
- Render.com account
- GitHub repository connected to Render
- Environment variables configured

#### Deploy to Render
```bash
# The render.yaml file handles automatic deployment
# Just push to your GitHub repository connected to Render

# Or use the deploy script:
./deploy.sh production render
```

#### Render Environment Variables
Set these in Render dashboard under Environment:
```bash
# Database (auto-provisioned by Render)
DATABASE_URL=postgresql://user:password@host:port/database

# Django Configuration
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=clm_backend.settings
DEBUG=False
ENVIRONMENT=production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key

# Cloudflare R2 Storage
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME=your-bucket-name

# Redis (if using Celery - optional)
REDIS_URL=redis://your-redis-url

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Render Post-Deployment Steps
```bash
# Run database migrations (via Render shell or dashboard)
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser

# Collect static files (if using Django static files)
python manage.py collectstatic --noinput
```

### Option edis://...

# Cloudflare R2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=your-bucket-name
R2_PUBLIC_URL=https://your-bucket.r2.cloudflarestorage.com

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Option 2: Docker Deployment (Recommended for Production)

#### Prerequisites
```bash
# Install Docker and Docker Compose
# macOS: https://docs.docker.com/docker-for-mac/install/
# Linux: https://docs.docker.com/engine/install/
```

#### Deploy with Docker
```bash
# Deploy to production
./deploy.sh production docker

# Or manually:
# 1. Build and start services
docker-compose up -d

# 2. Run migrations
docker-compose exec web python manage.py migrate

# 3. Create superuser
docker-compose exec web python manage.py createsuperuser

# 4. Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

#### Docker Commands
```bash
# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale worker=3

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

#### Production Docker Environment
Create `.env.prod` file:
```bash
# Django
DEBUG=False
SECRET_KEY=your-production-secret-key
DJANGO_SETTINGS_MODULE=clm_backend.settings

# Database
DB_NAME=clm_prod
DB_USER=clm_user
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Cloudflare R2 (same as development)
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=...
R2_PUBLIC_URL=...

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Option 3: AWS Deployment (Enterprise)

#### Prerequisites
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
```

#### Deploy to AWS
```bash
# Build and push to ECR
./deploy.sh production aws

# Manual steps for full AWS deployment:
# 1. Create ECR repository
aws ecr create-repository --repository-name clm-backend

# 2. Build and push Docker image
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1
docker tag clm-backend:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/clm-backend:latest
aws ecr get-login-password | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/clm-backend:latest

# 3. Deploy to ECS (requires additional setup)
# - Create ECS cluster
# - Create task definition
# - Create service
# - Configure ALB, RDS, ElastiCache
```

## 🔧 Configuration

### Environment Variables

#### Required for All Environments
```bash
# Django Core
DJANGO_SETTINGS_MODULE=clm_backend.settings
DEBUG=False
SECRET_KEY=your-secret-key-here

# Database
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=5432

# Cloudflare R2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=your-bucket-name
R2_PUBLIC_URL=https://your-bucket.r2.cloudflarestorage.com

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
```

#### Optional (Production)
```bash
# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://your-admin-domain.com

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### Database Setup

#### PostgreSQL Setup
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE clm_prod;
CREATE USER clm_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE clm_prod TO clm_user;
ALTER USER clm_user CREATEDB;
\q

# Run migrations
python manage.py migrate
```

#### Redis Setup
```bash
# Install Redis
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu

# Start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Application health
curl http://your-domain.com/api/health/

# Database connectivity
python manage.py dbshell --command="SELECT 1;"

# Redis connectivity
python manage.py shell -c "from django.core.cache import cache; cache.set('test', 'ok'); print(cache.get('test'))"
```

### Logs
```bash
# Django logs
tail -f logs/django.log

# Docker logs
docker-compose logs -f web

# Heroku logs
heroku logs --tail --app your-app-name
```

### Backups
```bash
# Database backup
pg_dump clm_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql clm_prod < backup_file.sql

# Automated backups (cron)
0 2 * * * pg_dump clm_prod > /backups/backup_$(date +\%Y\%m\%d).sql
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check database status
psql -h localhost -U clm_user -d clm_prod

# Test Django connection
python manage.py dbshell
```

#### 2. Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check permissions
chmod -R 755 staticfiles/
```

#### 3. Celery Not Working
```bash
# Check Redis connection
redis-cli ping

# Start Celery worker
celery -A clm_backend worker --loglevel=info

# Check Celery status
celery -A clm_backend inspect active
```

#### 4. File Upload Issues
```bash
# Check R2 credentials
python manage.py shell -c "
from authentication.r2_service import R2StorageService
r2 = R2StorageService()
print('R2 connection OK')
"

# Test file upload
curl -X POST -F "file=@test.txt" http://localhost:8000/api/contracts/
```

### Performance Tuning

#### Gunicorn Configuration
```python
# In settings.py or gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
worker_class = 'gthread'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 10
```

#### Database Optimization
```python
# Add database indexes
# Check settings.py DATABASES configuration
# Enable connection pooling
# Use read replicas for heavy reads
```

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs` or `heroku logs`
2. Verify environment variables
3. Test individual components
4. Check network connectivity
5. Review security groups/firewalls

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10.13'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: clm-backend-production
          heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

---

## 🎯 Quick Reference

### Development
```bash
./build.sh development
python manage.py runserver
```

### Production (Heroku)
```bash
./deploy.sh production heroku
```

### Production (Docker)
```bash
./deploy.sh production docker
```

### Production (AWS)
```bash
./deploy.sh production aws
```

### Health Check
```bash
curl http://your-domain.com/api/health/
```

### Logs
```bash
# Docker
docker-compose logs -f

# Heroku
heroku logs --tail
```

Happy deploying! 🚀