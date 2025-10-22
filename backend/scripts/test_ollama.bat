@echo off
echo Testing Ollama LLM Integration
echo ==============================

python backend/scripts/test_ollama.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All tests passed! Ollama is ready for use.
) else (
    echo.
    echo Some tests failed. Please check the configuration.
    echo For help, see: backend/scripts/README.md
)

pause
