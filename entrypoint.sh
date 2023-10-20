#!/bin/bash
#python app/manage.py makemigrations
python app/manage.py migrate                  # Apply database migrations
python app/manage.py collectstatic --noinput  # Collect static files

# Prepare log files
touch /gunicorn/logs/access.log
touch /gunicorn/logs/error.log

# Start Gunicorn processes
echo Starting Gunicorn.
cd /app/
exec gunicorn bdeliv.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level=info \
    --access-logfile=/gunicorn/logs/access.log \
    --error-logfile=/gunicorn/logs/error.log \
    --capture-output \
    "$@"