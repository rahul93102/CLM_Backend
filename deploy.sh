#!/bin/bash
# CLM Backend Build and Deploy Script
# Usage: ./deploy.sh [environment] [platform]
# Example: ./deploy.sh production heroku
# Example: ./deploy.sh staging docker

set -e

ENVIRONMENT=${1:-"production"}
PLATFORM=${2:-"docker"}
PROJECT_NAME="clm-backend"

echo "🚀 Starting deployment for $ENVIRONMENT environment on $PLATFORM"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    print_status "Running pre-deployment checks..."

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        exit 1
    fi

    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi

    # Check Python version
    python_version=$(python --version 2>&1 | awk '{print $2}')
    print_status "Python version: $python_version"

    # Run Django checks
    print_status "Running Django system checks..."
    python manage.py check --deploy

    # Run tests if in development
    if [ "$ENVIRONMENT" = "development" ]; then
        print_status "Running tests..."
        python manage.py test --verbosity=2
    fi

    print_status "Pre-deployment checks completed ✅"
}

# Build application
build_app() {
    print_status "Building application..."

    # Install dependencies
    pip install -r requirements.txt

    # Run migrations (dry run first)
    if [ "$ENVIRONMENT" = "production" ]; then
        print_status "Running database migrations..."
        python manage.py migrate --check
        if [ $? -ne 0 ]; then
            print_error "Pending migrations found! Run 'python manage.py migrate' first."
            exit 1
        fi
    else
        python manage.py migrate
    fi

    # Collect static files
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput --clear

    print_status "Build completed ✅"
}

# Deploy to Heroku
deploy_heroku() {
    print_status "Deploying to Heroku..."

    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI not found! Install it from https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi

    # Check if logged in to Heroku
    if ! heroku auth:whoami &> /dev/null; then
        print_error "Not logged in to Heroku! Run 'heroku login'"
        exit 1
    fi

    # Create Heroku app if it doesn't exist
    APP_NAME="${PROJECT_NAME}-${ENVIRONMENT}"
    if ! heroku apps:info --app="$APP_NAME" &> /dev/null; then
        print_status "Creating Heroku app: $APP_NAME"
        heroku create "$APP_NAME"
    fi

    # Set environment variables
    print_status "Setting environment variables..."
    heroku config:set --app="$APP_NAME" DJANGO_SETTINGS_MODULE=clm_backend.settings
    heroku config:set --app="$APP_NAME" DEBUG=False
    heroku config:set --app="$APP_NAME" SECRET_KEY="$(openssl rand -base64 32)"

    # Add buildpacks
    heroku buildpacks:add --app="$APP_NAME" heroku/python

    # Add Redis addon
    heroku addons:create --app="$APP_NAME" heroku-redis:hobby-dev

    # Add PostgreSQL addon
    heroku addons:create --app="$APP_NAME" heroku-postgresql:hobby-dev

    # Deploy
    print_status "Pushing to Heroku..."
    git push heroku main

    # Run migrations
    print_status "Running migrations on Heroku..."
    heroku run --app="$APP_NAME" python manage.py migrate

    # Create superuser (optional)
    read -p "Create superuser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        heroku run --app="$APP_NAME" python manage.py createsuperuser
    fi

    print_status "Heroku deployment completed ✅"
    print_status "App URL: https://$APP_NAME.herokuapp.com"
}

# Deploy with Docker
deploy_docker() {
    print_status "Deploying with Docker..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found! Install Docker from https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Build Docker image
    print_status "Building Docker image..."
    docker build -t "$PROJECT_NAME:$ENVIRONMENT" .

    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose down || true

    # Start services
    print_status "Starting services..."
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.yml up -d
    else
        docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
    fi

    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30

    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec web python manage.py migrate

    # Create superuser (optional)
    read -p "Create superuser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose exec web python manage.py createsuperuser
    fi

    print_status "Docker deployment completed ✅"
    print_status "Application running at: http://localhost:8000"
}

# Deploy to AWS
deploy_aws() {
    print_status "Deploying to AWS..."

    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found! Install it from https://aws.amazon.com/cli/"
        exit 1
    fi

    # Build and push to ECR
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    REGION=${AWS_REGION:-us-east-1}
    REPO_NAME="$PROJECT_NAME"

    # Create ECR repository if it doesn't exist
    aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$REGION" || \
    aws ecr create-repository --repository-name "$REPO_NAME" --region "$REGION"

    # Build and tag Docker image
    IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$ENVIRONMENT"
    docker build -t "$REPO_NAME" .
    docker tag "$REPO_NAME:latest" "$IMAGE_URI"

    # Authenticate Docker with ECR
    aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

    # Push image
    docker push "$IMAGE_URI"

    print_status "Docker image pushed to ECR: $IMAGE_URI"

    # Deploy to ECS/Fargate (would need additional setup)
    print_warning "For full AWS deployment, you need to:"
    print_warning "1. Create ECS cluster, task definition, and service"
    print_warning "2. Set up ALB, RDS, ElastiCache"
    print_warning "3. Configure security groups and IAM roles"
    print_warning "4. Set up CloudWatch logging and monitoring"

    print_status "AWS deployment preparation completed ✅"
}

# Main deployment logic
main() {
    case $PLATFORM in
        "heroku")
            pre_deployment_checks
            build_app
            deploy_heroku
            ;;
        "docker")
            pre_deployment_checks
            deploy_docker
            ;;
        "aws")
            pre_deployment_checks
            build_app
            deploy_aws
            ;;
        *)
            print_error "Unsupported platform: $PLATFORM"
            print_status "Supported platforms: heroku, docker, aws"
            exit 1
            ;;
    esac

    print_status "🎉 Deployment completed successfully!"
    print_status "Don't forget to:"
    print_status "  - Update your frontend to point to the new API URL"
    print_status "  - Configure domain and SSL certificates"
    print_status "  - Set up monitoring and logging"
    print_status "  - Configure backup strategies"
}

# Run main function
main "$@"