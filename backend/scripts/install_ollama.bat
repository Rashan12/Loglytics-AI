@echo off
echo Installing Ollama for Loglytics AI
echo ===================================

python backend/scripts/install_ollama.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Ollama installation completed!
    echo Next step: Run setup_ollama.bat
) else (
    echo.
    echo Installation failed. Please install Ollama manually.
    echo Download from: https://ollama.ai/download
)

pause
