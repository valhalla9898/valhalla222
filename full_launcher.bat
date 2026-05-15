@echo off
REM Wrapper to run the PowerShell full launcher with execution bypass
setlocal
set SCRIPTDIR=%~dp0
powershell -ExecutionPolicy Bypass -NoProfile -File "%SCRIPTDIR%full_launcher.ps1"
if errorlevel 1 (
    echo.
    echo Full launcher exited with error code %ERRORLEVEL%.
    pause
)
exit /b %ERRORLEVEL%
