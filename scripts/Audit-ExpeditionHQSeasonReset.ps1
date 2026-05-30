param(
  [string]$TaskName = "Expedition HQ Season 0.x Daily Reset",
  [switch]$NoSeasonPreview
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Invoker = Join-Path $PSScriptRoot "Invoke-ExpeditionHQSeasonRollover.ps1"
$RolloverScript = Join-Path $PSScriptRoot "rollover_season.py"

function Resolve-Python {
  $candidates = @(
    (Join-Path $Root ".venv\Scripts\python.exe"),
    (Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
  )

  foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }

  $command = Get-Command python -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }

  return $null
}

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
$taskInfo = $null
if ($task) {
  $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
}

$actions = @()
if ($task) {
  $actions = @($task.Actions | ForEach-Object {
    [pscustomobject]@{
      execute = $_.Execute
      arguments = $_.Arguments
    }
  })
}

$triggers = @()
if ($task) {
  $triggers = @($task.Triggers | ForEach-Object {
    [pscustomobject]@{
      enabled = $_.Enabled
      start_boundary = $_.StartBoundary
      type = $_.CimClass.CimClassName
    }
  })
}

$expectedActionPresent = @($actions | Where-Object {
  $_.execute -match "powershell(\.exe)?$" -and
  $_.arguments -like "*Invoke-ExpeditionHQSeasonRollover.ps1*" -and
  $_.arguments -like "*-Apply*"
}).Count -gt 0

$daily6amTriggerPresent = @($triggers | Where-Object {
  $_.enabled -and $_.start_boundary -match "T06:00:00"
}).Count -gt 0

$seasonPreview = $null
if (-not $NoSeasonPreview) {
  $python = Resolve-Python
  if ($python -and (Test-Path -LiteralPath $RolloverScript)) {
    $output = & $python $RolloverScript 2>&1
    $seasonPreview = [pscustomobject]@{
      command = "$python $RolloverScript"
      mutates_state = $false
      exit_code = $LASTEXITCODE
      output = ($output -join "`n")
    }
  } else {
    $seasonPreview = [pscustomobject]@{
      command = $null
      mutates_state = $false
      exit_code = $null
      output = "Python or rollover script not available for read-only preview."
    }
  }
}

[pscustomobject]@{
  source_of_truth = "windows_task_scheduler"
  codex_automation_role = "audit_report_only"
  mutates_state = $false
  task_name = $TaskName
  task_present = [bool]$task
  task_state = if ($task) { [string]$task.State } else { $null }
  last_run_time = if ($taskInfo) { $taskInfo.LastRunTime } else { $null }
  next_run_time = if ($taskInfo) { $taskInfo.NextRunTime } else { $null }
  last_task_result = if ($taskInfo) { $taskInfo.LastTaskResult } else { $null }
  expected_action_present = $expectedActionPresent
  daily_6am_trigger_present = $daily6amTriggerPresent
  compliant = [bool]($task -and $expectedActionPresent -and $daily6amTriggerPresent)
  actions = $actions
  triggers = $triggers
  season_preview = $seasonPreview
} | ConvertTo-Json -Depth 6
