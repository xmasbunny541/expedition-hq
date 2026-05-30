Option Explicit

Dim fso
Dim shell
Dim scriptDir
Dim watchScript
Dim keepAliveMinutes
Dim command

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
watchScript = fso.BuildPath(scriptDir, "Watch-ExpeditionHQ.ps1")
keepAliveMinutes = "5"

If WScript.Arguments.Count > 0 Then
  keepAliveMinutes = WScript.Arguments.Item(0)
End If

command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File " & _
  Chr(34) & watchScript & Chr(34) & " -KeepAliveMinutes " & keepAliveMinutes

shell.Run command, 0, False
