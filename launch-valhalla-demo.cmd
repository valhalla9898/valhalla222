@echo off
setlocal

set "PROJECT_DIR=%~dp0"
set "STREAMLIT_PORT=8501"
set "STREAMLIT_HOST=127.0.0.1"
set "DEMO_JSON=%PROJECT_DIR%demo\valhalla_onboarding.json"

cd /d "%PROJECT_DIR%"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )
)

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment is missing: venv\Scripts\activate.bat
    pause
    exit /b 1
)

if not exist "%DEMO_JSON%" (
    echo Demo data file not found: %DEMO_JSON%
    pause
    exit /b 1
)

echo Loading Valhalla demo data from:
	echo %DEMO_JSON%

echo Activating virtual environment...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate the virtual environment.
    pause
    exit /b 1
)

if not exist "venv\Scripts\streamlit.exe" (
    echo Installing project dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed.
        pause
        exit /b 1
    )
)

echo Starting Valhalla dashboard...
start "Valhalla Dashboard" cmd /k "cd /d \"%PROJECT_DIR%\" && call venv\Scripts\activate.bat && streamlit run app.py --server.address %STREAMLIT_HOST% --server.port %STREAMLIT_PORT% --server.headless false"

echo Waiting for dashboard to become ready...
powershell -NoProfile -Command "$deadline = (Get-Date).AddSeconds(90); while ((Get-Date) -lt $deadline) { try { $client = New-Object System.Net.Sockets.TcpClient('%STREAMLIT_HOST%', %STREAMLIT_PORT%); $client.Close(); Start-Process 'http://localhost:%STREAMLIT_PORT%'; exit 0 } catch { Start-Sleep -Seconds 1 } }; exit 1"

if errorlevel 1 (
    echo.
    echo Dashboard did not become ready in time.
    echo Please open http://localhost:%STREAMLIT_PORT% manually after a few seconds.
)

echo.
echo Valhalla demo launched.
echo Browser should open to http://localhost:%STREAMLIT_PORT%
echo.
exit /b 0
