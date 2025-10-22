@echo off
echo Testing Authentication System
echo =============================

python backend/scripts/test_auth.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All authentication tests passed!
) else (
    echo.
    echo Some authentication tests failed. Please check the logs.
)

pause
