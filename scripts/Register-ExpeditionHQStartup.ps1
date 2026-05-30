param(
  [string]$TaskName = "Expedition HQ Local Dashboard",
  [int]$KeepAliveMinutes = 5,
  [int]$RestartCount = 3,
  [int]$RestartIntervalMinutes = 1,
  [switch]$RunNow,
  [switch]$Unregister
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$StartScript = Join-Path $PSScriptRoot "Start-ExpeditionHQ.ps1"
$WatchScript = Join-Path $PSScriptRoot "Watch-ExpeditionHQ.ps1"
$LauncherScript = Join-Path $PSScriptRoot "Launch-ExpeditionHQWatcher.vbs"
$StartupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$StartupShortcut = Join-Path $StartupDir "Expedition HQ Local Dashboard.lnk"

if (-not (Test-Path -LiteralPath $StartScript)) {
  throw "Missing starter script: $StartScript"
}
if (-not (Test-Path -LiteralPath $WatchScript)) {
  throw "Missing watcher script: $WatchScript"
}
if (-not (Test-Path -LiteralPath $LauncherScript)) {
  throw "Missing launcher script: $LauncherScript"
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
  $shortcut.TargetPath = "wscript.exe"
  $shortcut.Arguments = "`"$LauncherScript`" $KeepAliveMinutes"
  $shortcut.WorkingDirectory = $Root
  $shortcut.WindowStyle = 7
  $shortcut.Description = "Keeps the local read-only Expedition HQ API and web dashboard running after user logon."
  $shortcut.Save()

  [pscustomobject]@{
    startup_shortcut = $StartupShortcut
    action = "powershell.exe $($shortcut.Arguments)"
  }
}

$quotedLauncher = '"' + $LauncherScript + '"'
$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "$quotedLauncher $KeepAliveMinutes"
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn
$keepAliveTrigger = New-ScheduledTaskTrigger -Daily -At 12:00am
$repeatingTemplate = New-ScheduledTaskTrigger -Once -At 12:00am `
  -RepetitionInterval (New-TimeSpan -Minutes $KeepAliveMinutes) `
  -RepetitionDuration (New-TimeSpan -Days 1)
$keepAliveTrigger.Repetition = $repeatingTemplate.Repetition
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
  -RestartCount $RestartCount `
  -RestartInterval (New-TimeSpan -Minutes $RestartIntervalMinutes) `
  -MultipleInstances IgnoreNew

$task = New-ScheduledTask -Action $action -Trigger @($logonTrigger, $keepAliveTrigger) -Principal $principal -Settings $settings `
  -Description "Keeps the local read-only Expedition HQ API and web dashboard running after user logon."

$result = $null
try {
  Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null

  if ($RunNow) {
    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 3
  }

  $removedStartupShortcut = $false
  if (Test-Path -LiteralPath $StartupShortcut) {
    Remove-Item -LiteralPath $StartupShortcut -Force
    $removedStartupShortcut = $true
  }

  $registered = Get-ScheduledTask -TaskName $TaskName
  $info = Get-ScheduledTaskInfo -TaskName $TaskName
  $result = [pscustomobject]@{
    method = "scheduled_task"
    task_name = $registered.TaskName
    state = $registered.State
    last_run_time = $info.LastRunTime
    last_task_result = $info.LastTaskResult
    keep_alive_minutes = $KeepAliveMinutes
    restart_count = $RestartCount
    restart_interval_minutes = $RestartIntervalMinutes
    startup_shortcut_removed = $removedStartupShortcut
    action = "wscript.exe $quotedLauncher $KeepAliveMinutes"
    root = $Root
  }
} catch {
  $shortcut = New-StartupShortcut
  if ($RunNow) {
    Start-Process -FilePath "wscript.exe" `
      -ArgumentList @(
        $LauncherScript,
        "$KeepAliveMinutes"
      ) `
      -WorkingDirectory $Root `
      -WindowStyle Hidden
    Start-Sleep -Seconds 3
  }

  $result = [pscustomobject]@{
    method = "startup_shortcut"
    reason = $_.Exception.Message
    startup_shortcut = $shortcut.startup_shortcut
    action = $shortcut.action
    keep_alive_minutes = $KeepAliveMinutes
    restart_count = $RestartCount
    restart_interval_minutes = $RestartIntervalMinutes
    root = $Root
  }
}

$result | ConvertTo-Json -Depth 4
