#!/bin/bash
# Start Flower (Celery Monitoring) for Loglytics AI

echo "Starting Flower..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Flower on port 5555
celery -A app.celery_app flower \
    --port=5555 \
    --address=0.0.0.0 \
    --url_prefix=flower

echo "Flower is running at http://localhost:5555"
echo "Press Ctrl+C to stop."
