#!/usr/bin/env pwsh
# Full launcher: creates venv, installs deps, runs tests, then launches app
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvDir = Join-Path $scriptDir 'venv'

Write-Host "[1/5] Checking Python and virtual environment..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not available on PATH. Please install Python 3.8+ and try again."
    exit 1
}

if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment..."
    & python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) { Write-Error 'Failed to create virtual environment'; exit 1 }
    Write-Host 'Virtual environment created'
} else {
    Write-Host "Virtual environment already exists"
}

$venvPython = Join-Path $venvDir 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment Python not found at $venvPython"
    exit 1
}

Write-Host "[2/5] Upgrading pip and installing dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $scriptDir 'requirements.txt')

Write-Host "[2.5/5] Ensuring Playwright browsers are installed (if Playwright present)..."
try {
    & $venvPython -m playwright --version | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host 'Playwright detected - installing browsers (this may take a while)'
        & $venvPython -m playwright install --with-deps
        if ($LASTEXITCODE -ne 0) { Write-Warning 'playwright install failed' }
        else { Write-Host 'Playwright browsers installed' }
    }
} catch {
    Write-Host 'Playwright not available via python -m playwright; skipping browser install'
}

Write-Host "[3/5] Verifying streamlit and pytest availability..."
& $venvPython -m pip show streamlit | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "streamlit not installed (may be optional)"
}

& $venvPython -m pip show pytest | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'pytest not installed - installing pytest'
    & $venvPython -m pip install pytest
    if ($LASTEXITCODE -ne 0) { Write-Warning "Failed to install pytest" }
}

Write-Host "[4/5] Running test suite (pytest) - skipping e2e tests..."
& $venvPython -m pytest -q -k "not e2e"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Tests failed (exit code $LASTEXITCODE). Aborting launch."
    exit 2
}

Write-Host '[5/5] Tests passed - launching application (no console will be left behind...)'

# Launch existing VBS launcher which runs start_login.bat (keeps UX consistent)
$startVbs = Join-Path $scriptDir 'START.vbs'
if (Test-Path $startVbs) {
    $wscript = Join-Path $env:SystemRoot 'System32\wscript.exe'
    & $wscript $startVbs
} else {
    Write-Warning "START.vbs not found; falling back to start_login.bat"
    $bat = Join-Path $scriptDir 'start_login.bat'
    if (Test-Path $bat) { Start-Process -FilePath $bat } else { Write-Error "No launcher found to start the app."; exit 3 }
}

Write-Host "Launcher finished."
