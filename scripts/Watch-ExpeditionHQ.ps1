param(
  [int]$ApiPort = 8789,
  [int]$WebPort = 5173,
  [int]$KeepAliveMinutes = 5,
  [switch]$Once
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$StartScript = Join-Path $PSScriptRoot "Start-ExpeditionHQ.ps1"
$RuntimeDir = Join-Path $Root "runtime"
$LogDir = Join-Path $RuntimeDir "logs"
$StatusPath = Join-Path $RuntimeDir "watcher-status.json"
$LogPath = Join-Path $LogDir "watcher.log"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

if (-not (Test-Path -LiteralPath $StartScript)) {
  throw "Missing starter script: $StartScript"
}

$createdNew = $false
$mutex = [System.Threading.Mutex]::new($true, "Local\ExpeditionHQLocalDashboardWatcher", [ref]$createdNew)
if (-not $createdNew) {
  if (-not (Test-Path -LiteralPath $StatusPath)) {
    [pscustomobject]@{
      updated_at = (Get-Date).ToString("o")
      status = "already_running"
      root = $Root
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $StatusPath -Encoding UTF8
  }
  exit 0
}

function Write-WatcherStatus {
  param(
    [Parameter(Mandatory = $true)][string]$Status,
    [int]$LastExitCode = 0,
    [string]$LastError = "",
    [string]$NextCheckAt = ""
  )

  [pscustomobject]@{
    updated_at = (Get-Date).ToString("o")
    status = $Status
    root = $Root
    url = "http://127.0.0.1:$WebPort/"
    api = "http://127.0.0.1:$ApiPort/"
    keep_alive_minutes = $KeepAliveMinutes
    last_exit_code = $LastExitCode
    last_error = $LastError
    next_check_at = $NextCheckAt
    log = $LogPath
  } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $StatusPath -Encoding UTF8
}

try {
  do {
    $startedAt = Get-Date
    Add-Content -LiteralPath $LogPath -Encoding UTF8 -Value "[$($startedAt.ToString("o"))] checking Expedition HQ"

    $output = $null
    $exitCode = 0
    try {
      $output = & $StartScript -ApiPort $ApiPort -WebPort $WebPort 2>&1
    } catch {
      $exitCode = 1
      $output = @($output, $_.Exception.Message) | Where-Object { $_ }
    }
    if ($output) {
      $output | ForEach-Object {
        Add-Content -LiteralPath $LogPath -Encoding UTF8 -Value $_
      }
    }

    if ($exitCode -eq 0) {
      $nextCheckAt = if ($Once) { "" } else { (Get-Date).AddMinutes($KeepAliveMinutes).ToString("o") }
      Write-WatcherStatus -Status "healthy" -LastExitCode 0 -NextCheckAt $nextCheckAt
    } else {
      Write-WatcherStatus -Status "start_failed" -LastExitCode $exitCode -LastError "Start-ExpeditionHQ.ps1 exited with $exitCode"
    }

    if ($Once) {
      exit $exitCode
    }

    Start-Sleep -Seconds ([Math]::Max(60, $KeepAliveMinutes * 60))
  } while ($true)
} finally {
  if ($createdNew) {
    $mutex.ReleaseMutex()
  }
  $mutex.Dispose()
}
