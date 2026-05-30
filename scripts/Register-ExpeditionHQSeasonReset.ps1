param(
  [string]$TaskName = "Expedition HQ Season 0.x Daily Reset",
  [switch]$RunNow,
  [switch]$Unregister
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Invoker = Join-Path $PSScriptRoot "Invoke-ExpeditionHQSeasonRollover.ps1"

if (-not (Test-Path -LiteralPath $Invoker)) {
  throw "Missing season rollover invoker: $Invoker"
}

if ($Unregister) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
  Write-Host "Removed scheduled task '$TaskName' if it existed."
  return
}

$quotedInvoker = '"' + $Invoker + '"'
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $quotedInvoker -Apply"
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00am
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
  -MultipleInstances IgnoreNew `
  -StartWhenAvailable

$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings `
  -Description "Non-destructively rolls Expedition HQ Season 0.x display windows at 6am local time."

Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null

if ($RunNow) {
  Start-ScheduledTask -TaskName $TaskName
  Start-Sleep -Seconds 3
}

$registered = Get-ScheduledTask -TaskName $TaskName
$info = Get-ScheduledTaskInfo -TaskName $TaskName
[pscustomobject]@{
  task_name = $registered.TaskName
  state = $registered.State
  last_run_time = $info.LastRunTime
  next_run_time = $info.NextRunTime
  last_task_result = $info.LastTaskResult
  action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $quotedInvoker -Apply"
  root = $Root
} | ConvertTo-Json -Depth 4
