@echo off
REM Start Celery Worker for Loglytics AI (Windows)

echo Starting Celery Worker...

REM Set Python path
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Start Celery worker
celery -A app.celery_app worker --loglevel=info --concurrency=4 --queues=default,high-priority,low-priority --pool=solo

pause
