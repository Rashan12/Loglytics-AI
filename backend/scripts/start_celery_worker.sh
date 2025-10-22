#!/bin/bash
# Start Celery Worker for Loglytics AI

echo "Starting Celery Worker..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Celery worker with specified queues
celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --queues=default,high-priority,low-priority \
    --logfile=logs/celery_worker.log \
    --pidfile=logs/celery_worker.pid

echo "Celery Worker stopped."
