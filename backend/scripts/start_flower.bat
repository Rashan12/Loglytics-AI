@echo off
REM Start Flower (Celery Monitoring) for Loglytics AI (Windows)

echo Starting Flower...
echo Flower will be available at http://localhost:5555

REM Set Python path
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Start Flower
celery -A app.celery_app flower --port=5555

pause
