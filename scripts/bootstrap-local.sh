#!/usr/bin/env bash
set -euo pipefail

echo "Validating seed files..."
python scripts/validate_seed.py

echo "Initializing local database..."
python scripts/init_db.py

echo "Next:"
echo "  API: cd apps/api && python -m uvicorn expedition_hq_api.main:app --reload --host 127.0.0.1 --port 8789"
echo "  Web: cd apps/web && npm install && npm run dev"
