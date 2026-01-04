# CLM Backend Makefile
.PHONY: help build deploy test clean setup

# Default target
help:
	@echo "CLM Backend Build & Deploy Commands"
	@echo ""
	@echo "Development:"
	@echo "  make setup          - Set up development environment"
	@echo "  make build-dev      - Build for development"
	@echo "  make run            - Run development server"
	@echo "  make test           - Run tests"
	@echo ""
	@echo "Production:"
	@echo "  make build-prod     - Build for production"
	@echo "  make deploy-heroku  - Deploy to Heroku"
	@echo "  make deploy-docker  - Deploy with Docker"
	@echo "  make deploy-aws     - Deploy to AWS"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean up build artifacts"
	@echo "  make migrate        - Run database migrations"
	@echo "  make superuser      - Create Django superuser"
	@echo "  make collectstatic  - Collect static files"
	@echo ""

# Setup development environment
setup:
	@echo "Setting up development environment..."
	python -m venv venv
	source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Development environment ready"

# Build commands
build-dev:
	./build.sh development

build-prod:
	./build.sh production

# Deploy commands
deploy-heroku:
	./deploy.sh production heroku

deploy-docker:
	./deploy.sh production docker

deploy-aws:
	./deploy.sh production aws

# Development commands
run:
	source venv/bin/activate && python manage.py runserver

test:
	source venv/bin/activate && python manage.py test --verbosity=2

migrate:
	source venv/bin/activate && python manage.py migrate

superuser:
	source venv/bin/activate && python manage.py createsuperuser

collectstatic:
	source venv/bin/activate && python manage.py collectstatic --noinput

# Maintenance
clean:
	@echo "Cleaning up..."
	rm -rf venv/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -f .coverage
	rm -f *.log
	@echo "✅ Cleanup completed"

# Docker commands
docker-build:
	docker build -t clm-backend:latest .

docker-run:
	docker-compose up -d

docker-logs:
	docker-compose logs -f

docker-stop:
	docker-compose down

# Heroku commands
heroku-logs:
	heroku logs --tail --app clm-backend-production

heroku-migrate:
	heroku run --app clm-backend-production python manage.py migrate

heroku-shell:
	heroku run --app clm-backend-production python manage.py shell

# Health checks
health:
	@echo "Checking application health..."
	@curl -s http://localhost:8000/api/health/ || echo "❌ Server not responding"
	@echo "✅ Health check completed"

# Full deployment pipeline
deploy: build-prod deploy-docker
	@echo "🎉 Full deployment completed!"

# Quick development setup
dev: setup build-dev run