@echo off
echo Testing RAG System
echo ===================

python backend/scripts/test_rag.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All RAG tests passed!
) else (
    echo.
    echo Some RAG tests failed. Please check the logs.
)

pause
