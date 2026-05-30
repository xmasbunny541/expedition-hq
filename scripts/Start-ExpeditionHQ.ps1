param(
  [int]$ApiPort = 8789,
  [int]$WebPort = 5173
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$RuntimeDir = Join-Path $Root "runtime"
$LogDir = Join-Path $RuntimeDir "logs"
$StatusPath = Join-Path $RuntimeDir "status.json"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

function Resolve-Tool {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string[]]$Candidates
  )

  foreach ($candidate in $Candidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }

  $command = Get-Command $Name -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }

  throw "Could not find $Name. Checked: $($Candidates -join ', ')"
}

function Test-LocalPort {
  param([Parameter(Mandatory = $true)][int]$Port)

  $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    Select-Object -First 1
  return $null -ne $listener
}

function Get-ListeningProcessId {
  param([Parameter(Mandatory = $true)][int]$Port)

  $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    Select-Object -First 1
  if ($listener) {
    return $listener.OwningProcess
  }
  return $null
}

function Test-HttpEndpoint {
  param(
    [Parameter(Mandatory = $true)][string]$Uri,
    [string]$ExpectedContent = ""
  )

  try {
    $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 300) {
      return $false
    }
    if ($ExpectedContent -and -not $response.Content.Contains($ExpectedContent)) {
      return $false
    }
    return $true
  } catch {
    return $false
  }
}

function Wait-HttpEndpoint {
  param(
    [Parameter(Mandatory = $true)][string]$Uri,
    [string]$ExpectedContent = "",
    [int]$TimeoutSeconds = 25
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    if (Test-HttpEndpoint -Uri $Uri -ExpectedContent $ExpectedContent) {
      return $true
    }
    Start-Sleep -Milliseconds 500
  }
  return $false
}

function Start-LocalService {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][int]$Port,
    [Parameter(Mandatory = $true)][string]$FilePath,
    [Parameter(Mandatory = $true)][string[]]$ArgumentList,
    [Parameter(Mandatory = $true)][string]$WorkingDirectory,
    [Parameter(Mandatory = $true)][string]$LogBase,
    [Parameter(Mandatory = $true)][string]$HealthUri,
    [string]$HealthContains = ""
  )

  if (Test-LocalPort -Port $Port) {
    $ready = Wait-HttpEndpoint -Uri $HealthUri -ExpectedContent $HealthContains -TimeoutSeconds 10
    return [pscustomobject]@{
      name = $Name
      port = $Port
      status = if ($ready) { "already_healthy" } else { "port_occupied_unhealthy" }
      pid = Get-ListeningProcessId -Port $Port
      health = $HealthUri
    }
  }

  $stdout = Join-Path $LogDir "$LogBase.out.log"
  $stderr = Join-Path $LogDir "$LogBase.err.log"
  $process = Start-Process -FilePath $FilePath `
    -ArgumentList $ArgumentList `
    -WorkingDirectory $WorkingDirectory `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -PassThru

  $ready = Wait-HttpEndpoint -Uri $HealthUri -ExpectedContent $HealthContains
  [pscustomobject]@{
    name = $Name
    port = $Port
    status = if ($ready) { "healthy" } else { "not_ready" }
    pid = $process.Id
    health = $HealthUri
    stdout = $stdout
    stderr = $stderr
  }
}

$python = Resolve-Tool -Name "python" -Candidates @(
  (Join-Path $Root ".venv\Scripts\python.exe"),
  (Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
)

$node = Resolve-Tool -Name "node" -Candidates @(
  (Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
)

$vite = Join-Path $Root "apps\web\node_modules\vite\bin\vite.js"
if (-not (Test-Path -LiteralPath $vite)) {
  throw "Vite is not installed at $vite. Run npm install in apps\web before registering startup."
}

$apiArgs = @(
  "-m", "uvicorn",
  "expedition_hq_api.main:app",
  "--app-dir", "apps/api",
  "--host", "127.0.0.1",
  "--port", "$ApiPort"
)

$webArgs = @(
  $vite,
  "--host", "127.0.0.1",
  "--port", "$WebPort",
  "--strictPort"
)

$apiHealth = "http://127.0.0.1:$ApiPort/health"
$webHealth = "http://127.0.0.1:$WebPort/"

$results = @(
  Start-LocalService -Name "api" -Port $ApiPort -FilePath $python -ArgumentList $apiArgs -WorkingDirectory $Root -LogBase "api" -HealthUri $apiHealth -HealthContains "expedition-hq-api"
  Start-LocalService -Name "web" -Port $WebPort -FilePath $node -ArgumentList $webArgs -WorkingDirectory (Join-Path $Root "apps\web") -LogBase "web" -HealthUri $webHealth -HealthContains '<div id="root"></div>'
)

$status = [pscustomobject]@{
  updated_at = (Get-Date).ToString("o")
  root = $Root
  url = "http://127.0.0.1:$WebPort/"
  api = "http://127.0.0.1:$ApiPort/"
  services = $results
}

$status | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $StatusPath -Encoding UTF8
$status | ConvertTo-Json -Depth 6

$unhealthy = @($results | Where-Object { $_.status -notin @("healthy", "already_healthy") })
if ($unhealthy.Count -gt 0) {
  exit 1
}
