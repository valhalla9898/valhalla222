@echo off
REM Agentic-IAM One-Click Launcher
REM Complete setup and launch in one click

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ================================================================
echo          AGENTIC-IAM v2.0 - ONE-CLICK LAUNCHER
echo ================================================================
echo.

REM Check if venv exists
if not exist ".\venv\" (
    echo [1/4] Creating Python virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo [2/4] Installing dependencies...
call ".\venv\Scripts\activate.bat"
python -m pip install -q -r requirements.txt >nul 2>&1

echo [3/4] Installing Playwright browsers...
python -m playwright install chromium >nul 2>&1

echo [4/4] Launching Agentic-IAM Dashboard...
echo.
echo ================================================================
echo The app will open in your browser at: http://localhost:8501
echo ================================================================
echo.
echo Default Credentials:
echo   Admin:    admin / admin123
echo   Operator: operator / operator123
echo   User:     user / user123
echo.
echo Waiting for server to start (3 seconds)...
timeout /t 3 /nobreak >nul

REM Open browser
start http://localhost:8501

REM Start the app
python -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1
