# Create Desktop Shortcut for Agentic-IAM Full Launcher (runs setup, tests, then app)

$desktopPath = [Environment]::GetFolderPath('Desktop')
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$shortcutPath = Join-Path $desktopPath 'Agentic-IAM - Full Launcher.lnk'

$WshShell = New-Object -ComObject WScript.Shell

$shortcut = $WshShell.CreateShortcut($shortcutPath)
$vbsLauncher = Join-Path $scriptDir 'FULL_START.vbs'
$wscript = Join-Path $env:SystemRoot 'System32\wscript.exe'

$shortcut.TargetPath = $wscript
$shortcut.Arguments  = "`"$vbsLauncher`""
$shortcut.WorkingDirectory = $scriptDir
$shortcut.Description = "One-click: setup env, run tests, and launch Agentic-IAM"
$shortcut.IconLocation = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe,0"

$shortcut.Save()

Write-Host "✅ Full desktop shortcut created:" -ForegroundColor Green
Write-Host "  $shortcutPath" -ForegroundColor Cyan
