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

function Wait-LocalPort {
  param(
    [Parameter(Mandatory = $true)][int]$Port,
    [int]$TimeoutSeconds = 25
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    if (Test-LocalPort -Port $Port) {
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
    [Parameter(Mandatory = $true)][string]$LogBase
  )

  if (Test-LocalPort -Port $Port) {
    return [pscustomobject]@{
      name = $Name
      port = $Port
      status = "already_listening"
      pid = $null
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

  $ready = Wait-LocalPort -Port $Port
  [pscustomobject]@{
    name = $Name
    port = $Port
    status = if ($ready) { "listening" } else { "not_ready" }
    pid = $process.Id
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
  "--port", "$WebPort"
)

$results = @(
  Start-LocalService -Name "api" -Port $ApiPort -FilePath $python -ArgumentList $apiArgs -WorkingDirectory $Root -LogBase "api"
  Start-LocalService -Name "web" -Port $WebPort -FilePath $node -ArgumentList $webArgs -WorkingDirectory (Join-Path $Root "apps\web") -LogBase "web"
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

if ($results.status -contains "not_ready") {
  exit 1
}
