param(
  [string]$TaskName = "Expedition HQ Local Dashboard",
  [switch]$RunNow,
  [switch]$Unregister
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$StartScript = Join-Path $PSScriptRoot "Start-ExpeditionHQ.ps1"
$StartupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$StartupShortcut = Join-Path $StartupDir "Expedition HQ Local Dashboard.lnk"

if (-not (Test-Path -LiteralPath $StartScript)) {
  throw "Missing starter script: $StartScript"
}

if ($Unregister) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath $StartupShortcut -Force -ErrorAction SilentlyContinue
  Write-Host "Removed scheduled task '$TaskName' and startup shortcut if they existed."
  return
}

function New-StartupShortcut {
  New-Item -ItemType Directory -Path $StartupDir -Force | Out-Null
  $shell = New-Object -ComObject WScript.Shell
  $shortcut = $shell.CreateShortcut($StartupShortcut)
  $shortcut.TargetPath = "powershell.exe"
  $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$StartScript`""
  $shortcut.WorkingDirectory = $Root
  $shortcut.WindowStyle = 7
  $shortcut.Description = "Starts the local read-only Expedition HQ API and web dashboard at user logon."
  $shortcut.Save()

  [pscustomobject]@{
    startup_shortcut = $StartupShortcut
    action = "powershell.exe $($shortcut.Arguments)"
  }
}

$quotedScript = '"' + $StartScript + '"'
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File $quotedScript"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -ExecutionTimeLimit (New-TimeSpan -Hours 8) `
  -MultipleInstances IgnoreNew

$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings `
  -Description "Starts the local read-only Expedition HQ API and web dashboard at user logon."

$result = $null
try {
  Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null

  if ($RunNow) {
    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 3
  }

  $registered = Get-ScheduledTask -TaskName $TaskName
  $info = Get-ScheduledTaskInfo -TaskName $TaskName
  $result = [pscustomobject]@{
    method = "scheduled_task"
    task_name = $registered.TaskName
    state = $registered.State
    last_run_time = $info.LastRunTime
    last_task_result = $info.LastTaskResult
    action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File $quotedScript"
    root = $Root
  }
} catch {
  $shortcut = New-StartupShortcut
  if ($RunNow) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $StartScript | Out-Null
  }

  $result = [pscustomobject]@{
    method = "startup_shortcut"
    reason = $_.Exception.Message
    startup_shortcut = $shortcut.startup_shortcut
    action = $shortcut.action
    root = $Root
  }
}

$result | ConvertTo-Json -Depth 4
