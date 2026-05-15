@echo off
REM Agentic-IAM Direct Launcher - Quick Start
REM This launcher starts the app directly without lengthy setup

cd /d "%~dp0"

echo.
echo ================================================================
echo                   AGENTIC-IAM LAUNCHER
echo ================================================================
echo.
echo Activating virtual environment and starting Streamlit...
echo.

REM Activate venv and run streamlit directly
call ".\venv\Scripts\activate.bat"

REM Launch Streamlit on port 8501
python -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1

pause
