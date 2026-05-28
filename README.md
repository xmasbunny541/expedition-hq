# Expedition HQ Codex Starter

Local-first starter scaffold for building **Expedition HQ**: a read-only, living visual dashboard for observing August's AI/Codex/OpenClaw ecosystem.

## What this starter contains

- Codex project instructions in `AGENTS.md`
- Security and non-goal guardrails
- Redacted agent census import
- Seed rosters for agents, expeditions, routes, memory stores, blockers, events, and milestones
- FastAPI + SQLite backend skeleton
- Vite + React frontend skeleton
- JSON schema and TypeScript type starter
- Hook/skill placeholders for future OpenClaw/Codex integration
- Field report and milestone archive folders

## Recommended first commits

1. `Initialize Expedition HQ project shell and guardrails`
2. `Define Expedition HQ charter and success criteria`
3. `Import sanitized ecosystem census and initial expedition map`

## First run target

Start read-only. The MVP should show:
- Specialist roster
- Expedition board
- Field reports
- Milestone gallery
- Static/seed-driven Bureau HQ visual state

Do not add live control actions until the read-only observability layer is stable.

## Local Windows runbook

Prerequisites:
- Python 3.11 or newer available as `python`
- Node.js and npm available on PATH

If Node was just installed with `winget`, open a new PowerShell window before running npm commands so the updated PATH is loaded.

API setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r apps/api/requirements-dev.txt
python scripts/validate_seed.py
python scripts/init_db.py
python -m uvicorn expedition_hq_api.main:app --app-dir apps/api --reload --host 127.0.0.1 --port 8789
```

Web setup:

```powershell
cd apps/web
npm install
npm run dev
```

Open the dashboard at `http://127.0.0.1:5173`. The web app expects the API at `http://127.0.0.1:8789` unless `VITE_API_BASE` is set.

Verification:

```powershell
python scripts/validate_seed.py
python scripts/init_db.py
python -m pytest apps/api/tests
cd apps/web
npm run build
```

The API is read-only except for local SQLite event ingestion through `POST /events`. Reseeding is intentionally a local script operation, not a public API route.
