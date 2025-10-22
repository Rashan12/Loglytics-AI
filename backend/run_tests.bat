@echo off
echo ==========================================
echo Loglytics AI - End-to-End Backend Tests
echo ==========================================
echo.

REM Check if backend is running
echo Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend is not running!
    echo Please start the backend first:
    echo   python -m uvicorn app.main:app --reload
    pause
    exit /b 1
)

echo ✅ Backend is running
echo.

REM Install test dependencies
echo Installing test dependencies...
pip install -r requirements-test.txt
echo.

REM Run tests
echo Running comprehensive tests...
pytest tests/test_end_to_end.py -v -s --tb=short

REM Display results
echo.
echo ==========================================
echo Test Results Saved to: TEST_RESULTS.md
echo ==========================================
pause
