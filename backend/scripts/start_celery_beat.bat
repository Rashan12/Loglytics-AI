@echo off
REM Start Celery Beat (Scheduler) for Loglytics AI (Windows)

echo Starting Celery Beat...

REM Set Python path
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Start Celery beat
celery -A app.celery_app beat --loglevel=info

pause
