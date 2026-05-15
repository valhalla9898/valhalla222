' Auto-open browser when Streamlit is ready
' This script monitors port 8501 and opens the browser automatically

Set objShell = CreateObject("WScript.Shell")
Set objHttp = CreateObject("MSXML2.XMLHTTP")

' Give server 3 seconds to start
WScript.Sleep 3000

' Try to open browser
strURL = "http://localhost:8501"
objShell.Run "explorer.exe " & strURL, 1, False

' Keep script alive briefly
WScript.Sleep 1000
