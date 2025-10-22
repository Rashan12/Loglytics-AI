@echo off
echo Testing LLM Service
echo ===================

python backend/scripts/test_llm.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All LLM tests passed!
) else (
    echo.
    echo Some LLM tests failed. Please check the logs.
)

pause
