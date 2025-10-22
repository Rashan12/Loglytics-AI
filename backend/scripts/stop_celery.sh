#!/bin/bash
# Stop all Celery processes for Loglytics AI

echo "Stopping Celery processes..."

# Stop worker
if [ -f logs/celery_worker.pid ]; then
    kill -TERM $(cat logs/celery_worker.pid)
    echo "Celery worker stopped."
    rm logs/celery_worker.pid
fi

# Stop beat
if [ -f logs/celery_beat.pid ]; then
    kill -TERM $(cat logs/celery_beat.pid)
    echo "Celery beat stopped."
    rm logs/celery_beat.pid
fi

# Alternatively, kill all celery processes
# pkill -f "celery.*app.celery_app"

echo "All Celery processes stopped."
