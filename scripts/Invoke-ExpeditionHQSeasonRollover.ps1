param(
  [switch]$Apply,
  [string]$Now
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$RuntimeDir = Join-Path $Root "runtime"
$LogDir = Join-Path $RuntimeDir "logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

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

  throw "Could not find python."
}

$python = Resolve-Python
$rolloverScript = Join-Path $PSScriptRoot "rollover_season.py"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logPath = Join-Path $LogDir "season-rollover-$timestamp.log"
$arguments = @($rolloverScript)

if ($Apply) {
  $arguments += "--apply"
}
if ($Now) {
  $arguments += @("--now", $Now)
}

& $python @arguments *>&1 | Tee-Object -FilePath $logPath
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
