#!/usr/bin/env bash
set -euo pipefail

echo "Validating seed files..."
"${PYTHON:-python3}" scripts/validate_seed.py

echo "Initializing local database..."
"${PYTHON:-python3}" scripts/init_db.py

echo "Next:"
echo "  API: ${PYTHON:-python3} -m uvicorn expedition_hq_api.main:app --app-dir apps/api --reload --host 127.0.0.1 --port 8789"
echo "  Web: cd apps/web && npm install && npm run dev"
