# Create Desktop Shortcut with Admin Privileges for Agentic-IAM

# Get paths
$desktopPath = [Environment]::GetFolderPath('Desktop')
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$shortcutPath = "$desktopPath\Agentic-IAM (Admin).lnk"
$launcherPath = "$scriptDir\full_launcher.ps1"

# Create WScript Shell object
$WshShell = New-Object -ComObject WScript.Shell

# Create the shortcut pointing to PowerShell with Admin execution
$shortcut = $WshShell.CreateShortcut($shortcutPath)

# Use PowerShell as target with NoExit to run launcher script with Admin
$shortcut.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$shortcut.Arguments = "-NoExit -ExecutionPolicy RemoteSigned -Command `"Set-Location '$scriptDir'; & '.\full_launcher.ps1'`""
$shortcut.WorkingDirectory = $scriptDir
$shortcut.Description = "Launch Agentic-IAM with Admin Privileges"
$shortcut.IconLocation = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe,0"

# IMPORTANT: Set to run as Administrator
# This requires modifying the shortcut file directly
$shortcut.Save()

# Now modify the shortcut to run as Administrator (requires admin privileges)
# We use a workaround with attrib command
$bytes = [System.IO.File]::ReadAllBytes($shortcutPath)
# Set the "Run as Administrator" flag (byte at position 0x15, set bit 0x20)
$bytes[0x15] = $bytes[0x15] -bor 0x20
[System.IO.File]::WriteAllBytes($shortcutPath, $bytes)

Write-Host "✅ Admin Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Name: Agentic-IAM (Admin)" -ForegroundColor Cyan
Write-Host "Location: $shortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  When you click the shortcut, Windows will ask for Admin confirmation." -ForegroundColor Yellow
Write-Host "Click 'Yes' to run with administrator privileges." -ForegroundColor Yellow
