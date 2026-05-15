' Full silent launcher for the full_launcher.bat
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Path to the full launcher batch file
launcherPath = scriptPath & "\full_launcher.bat"

if objFSO.FileExists(launcherPath) then
    ' Run with normal window so user can see progress
    objShell.Run """" & launcherPath & """", 1, False
else
    objShell.Popup "Error: full_launcher.bat not found in " & scriptPath, 0, "Agentic-IAM Full Launcher Error", 16
end if
