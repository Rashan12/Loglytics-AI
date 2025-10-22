#!/bin/bash
# Start Celery Beat (Scheduler) for Loglytics AI

echo "Starting Celery Beat..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Celery beat scheduler
celery -A app.celery_app beat \
    --loglevel=info \
    --logfile=logs/celery_beat.log \
    --pidfile=logs/celery_beat.pid

echo "Celery Beat stopped."
