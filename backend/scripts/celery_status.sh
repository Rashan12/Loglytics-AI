#!/bin/bash
# Check Celery status for Loglytics AI

echo "=== Celery Status ==="
echo ""

# Check worker status
echo "Worker Status:"
celery -A app.celery_app inspect active
echo ""

# Check scheduled tasks
echo "Scheduled Tasks (Beat):"
celery -A app.celery_app inspect scheduled
echo ""

# Check registered tasks
echo "Registered Tasks:"
celery -A app.celery_app inspect registered
echo ""

# Check stats
echo "Worker Stats:"
celery -A app.celery_app inspect stats
echo ""

# Check if Redis is accessible
echo "Redis Connection:"
redis-cli ping
echo ""

echo "=== Status Check Complete ==="
