#!/bin/bash
# CLM Backend Build Script
# Usage: ./build.sh [environment]
# Example: ./build.sh production

set -e

ENVIRONMENT=${1:-"development"}

echo "🔨 Building CLM Backend for $ENVIRONMENT environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create virtual environment if it doesn't exist
setup_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python -m venv venv
    fi

    print_status "Activating virtual environment..."
    source venv/bin/activate
}

# Install dependencies
install_deps() {
    print_status "Installing dependencies..."

    if [ "$ENVIRONMENT" = "production" ]; then
        # Install production dependencies only
        pip install --upgrade pip setuptools wheel

        # Install build dependencies first (helps with Pillow compilation)
        pip install --upgrade pip
        pip install setuptools>=65.0.0 wheel>=0.37.0

        # Install requirements
        pip install -r requirements.txt --no-cache-dir
    else
        # Install all dependencies including dev tools
        pip install --upgrade pip setuptools wheel
        pip install -r requirements.txt

        # Install additional dev dependencies
        pip install --upgrade pip
        pip install black isort flake8 mypy pytest pytest-django pytest-cov
    fi
}

# Run code quality checks
code_quality() {
    if [ "$ENVIRONMENT" = "development" ]; then
        print_status "Running code quality checks..."

        # Format code
        print_status "Formatting code with Black..."
        black . --exclude="venv/|__pycache__/|\.git/|migrations/"

        # Sort imports
        print_status "Sorting imports with isort..."
        isort . --skip="venv" --skip="__pycache__" --skip=".git" --skip="migrations"

        # Lint code
        print_status "Linting with flake8..."
        flake8 . --exclude="venv,__pycache__,.git,migrations" --max-line-length=88

        # Type checking (optional)
        print_status "Type checking with mypy..."
        mypy . --ignore-missing-imports --exclude="venv|__pycache__|migrations" || true
    fi
}

# Run tests
run_tests() {
    print_status "Running tests..."

    if [ "$ENVIRONMENT" = "production" ]; then
        # Run tests without coverage in production
        python manage.py test --verbosity=1
    else
        # Run tests with coverage in development
        python manage.py test --verbosity=2 --parallel 1
        # pytest --cov=. --cov-report=html --cov-report=term
    fi
}

# Database operations
setup_database() {
    print_status "Setting up database..."

    # Run migrations
    python manage.py migrate

    # Create superuser if needed
    if [ "$ENVIRONMENT" = "development" ]; then
        print_status "Checking for superuser..."
        python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
    fi
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput --clear
}

# Build Docker image
build_docker() {
    if [ "$ENVIRONMENT" = "production" ]; then
        print_status "Building Docker image..."
        docker build -t clm-backend:latest .
        docker tag clm-backend:latest clm-backend:$ENVIRONMENT
    fi
}

# Create deployment package
create_package() {
    if [ "$ENVIRONMENT" = "production" ]; then
        print_status "Creating deployment package..."

        # Create dist directory
        mkdir -p dist

        # Copy necessary files
        rsync -av --exclude='venv/' --exclude='__pycache__/' --exclude='.git/' \
              --exclude='*.pyc' --exclude='.env' --exclude='dist/' \
              --exclude='*.log' --exclude='htmlcov/' --exclude='.coverage' \
              . dist/

        # Create tarball
        tar -czf "clm-backend-$ENVIRONMENT-$(date +%Y%m%d-%H%M%S).tar.gz" dist/
        rm -rf dist

        print_status "Deployment package created"
    fi
}

# Main build process
main() {
    print_status "Starting build process for $ENVIRONMENT..."

    # Setup
    setup_venv
    install_deps

    # Code quality (development only)
    code_quality

    # Tests
    run_tests

    # Database
    setup_database

    # Static files
    collect_static

    # Docker (production only)
    build_docker

    # Package (production only)
    create_package

    print_status "✅ Build completed successfully!"

    if [ "$ENVIRONMENT" = "development" ]; then
        print_status "🚀 Starting development server..."
        print_status "Run: python manage.py runserver"
        print_status "Or: ./deploy.sh development docker"
    else
        print_status "📦 Ready for deployment!"
        print_status "Run: ./deploy.sh production [platform]"
    fi
}

# Run main function
main "$@"