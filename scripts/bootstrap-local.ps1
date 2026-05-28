$ErrorActionPreference = "Stop"

Write-Host "Validating seed files..."
python scripts/validate_seed.py

Write-Host "Initializing local database..."
python scripts/init_db.py

Write-Host "Next:"
Write-Host "  API: cd apps/api; python -m uvicorn expedition_hq_api.main:app --reload --host 127.0.0.1 --port 8789"
Write-Host "  Web: cd apps/web; npm install; npm run dev"
