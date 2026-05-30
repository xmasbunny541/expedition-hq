$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
  $command = Get-Command python -ErrorAction SilentlyContinue
  if (-not $command) {
    throw "Could not find .venv Python or python on PATH."
  }
  $Python = $command.Source
}

Write-Host "Validating seed files..."
& $Python scripts/validate_seed.py

Write-Host "Initializing local database..."
& $Python scripts/init_db.py

Write-Host "Next:"
Write-Host "  API: .\.venv\Scripts\python.exe -m uvicorn expedition_hq_api.main:app --app-dir apps/api --reload --host 127.0.0.1 --port 8789"
Write-Host "  Web: cd apps/web; npm.cmd install; npm.cmd run dev"
