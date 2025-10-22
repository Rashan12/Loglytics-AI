@echo off
echo Starting Ollama LLM Setup for Loglytics AI
echo ==========================================

python backend/scripts/setup_ollama.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Setup completed successfully!
    echo You can now test the installation with:
    echo python backend/scripts/test_ollama.py
) else (
    echo.
    echo Setup failed. Please check the error messages above.
    echo For help, see: backend/scripts/README.md
)

pause
