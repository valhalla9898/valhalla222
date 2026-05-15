@echo off
REM Quick Start Script for Agentic-IAM with Login System
REM Run this to start the application

echo.
echo ================================================================
echo              AGENTIC-IAM - LOGIN SYSTEM
echo ================================================================
echo.
echo Starting Agentic-IAM Dashboard with Authentication...
echo.
echo Default Credentials:
echo   Admin: admin / admin123
echo   User:  user / user123
echo.
echo IMPORTANT: Change these passwords after first login!
echo.
echo ================================================================
echo.

REM Use venv Python directly (bypass Windows Store alias)
set PYTHON="%~dp0.venv\Scripts\python.exe"

REM Change to script directory to ensure relative imports work
cd /d "%~dp0"

REM Run the dashboard directly so the onboarding screen always appears
%PYTHON% -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless false

pause
