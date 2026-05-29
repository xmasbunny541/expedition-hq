# Expedition HQ Codex Starter

Local-first starter scaffold for building **Expedition HQ**: a read-only, living visual dashboard for observing August's AI/Codex/OpenClaw ecosystem.

## What this starter contains

- Codex project instructions in `AGENTS.md`
- Security and non-goal guardrails
- Agent XP status plan and gamification rules
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

Season 0.x cross-project XP claims can be submitted to the local API with evidence:

```powershell
python scripts/log_xp_claim.py --source-id openclaw-main --expedition-id expedition-hq-dashboard --title "Claim title" --summary "What useful work happened and why it matters." --active-minutes 30 --evidence "path/or/result"
```

Persistent local startup:

```powershell
.\scripts\Start-ExpeditionHQ.ps1
.\scripts\Register-ExpeditionHQStartup.ps1 -RunNow
```

The startup entry is per-user and local-only. It starts the read-only API on `127.0.0.1:8789` and the web dashboard on `127.0.0.1:5173` at Windows logon. The installer uses Task Scheduler when permitted and falls back to a Startup-folder shortcut when Windows blocks scheduled task registration. Runtime logs and status are written under ignored `runtime/` files.

Verification:

```powershell
python scripts/validate_seed.py
python scripts/init_db.py
python -m pytest apps/api/tests
cd apps/web
npm run build
```

The API is read-only except for local SQLite event/XP-claim ingestion through `POST /events` and `POST /xp-claims`. Reseeding is intentionally a local script operation, not a public API route.
