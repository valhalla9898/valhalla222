@echo off
REM Admin Launcher for Agentic-IAM
REM This batch file automatically elevates to admin privileges

setlocal enabledelayedexpansion

REM Check if running with admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    REM Not admin, so request elevation
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c %~s0' -Verb RunAs"
    exit /b
)

REM Now running with admin privileges
echo ✓ Running with Administrator Privileges
cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the Streamlit app
echo.
echo Starting Agentic-IAM Dashboard...
echo.

streamlit run app.py --logger.level=info

pause
