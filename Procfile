# Heroku Procfile for CLM Backend
web: gunicorn clm_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 2 --timeout 30
worker: celery -A clm_backend worker --loglevel=info
beat: celery -A clm_backend beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
