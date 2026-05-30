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
On this Windows workstation, the most reliable commands are the explicit repo venv Python and `npm.cmd`; plain `python` may resolve to the Microsoft Store alias and plain PowerShell `npm` may hit script execution policy.

API setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r apps/api/requirements-dev.txt
.\.venv\Scripts\python.exe scripts\validate_seed.py
.\.venv\Scripts\python.exe scripts\init_db.py
.\.venv\Scripts\python.exe -m uvicorn expedition_hq_api.main:app --app-dir apps/api --reload --host 127.0.0.1 --port 8789
```

Web setup:

```powershell
cd apps/web
npm.cmd install
npm.cmd run dev
```

Open the dashboard at `http://127.0.0.1:5173`. The web app expects the API at `http://127.0.0.1:8789` unless `VITE_API_BASE` is set. Visiting `http://127.0.0.1:8789/` redirects to the dashboard so the API root is not a dead-looking page.

Season 0.x cross-project XP claims can be submitted to the local API with evidence:

```powershell
.\.venv\Scripts\python.exe scripts\log_xp_claim.py --source-id openclaw-main --expedition-id expedition-hq-dashboard --title "Claim title" --summary "What useful work happened and why it matters." --active-minutes 30 --evidence "path/or/result"
```

Persistent local startup:

```powershell
.\scripts\Start-ExpeditionHQ.ps1
.\scripts\Register-ExpeditionHQStartup.ps1 -RunNow
```

The startup entry is per-user and local-only. Task Scheduler runs a hidden `wscript.exe` launcher at Windows logon and every five minutes. The launcher starts `scripts\Watch-ExpeditionHQ.ps1` only when the watcher is not already running; the watcher starts or verifies the read-only API on `127.0.0.1:8789` and the web dashboard on `127.0.0.1:5173`. The installer falls back to a Startup-folder shortcut when Windows blocks scheduled task registration. The watcher writes `runtime\watcher-status.json`; the service launcher writes `runtime\status.json`.

Verification:

```powershell
npm.cmd run seed:validate
npm.cmd run api:test
npm.cmd run web:build
```

The npm verification scripts use the repo-local Python runner, avoid the Windows Store `python` alias, and keep pytest temp/cache output under ignored `runtime/` paths. Use the direct venv commands above when you are actively debugging setup; use the npm scripts for routine checks and overnight automation reports.

The API is read-only except for local SQLite event/XP-claim ingestion through `POST /events` and `POST /xp-claims`. Reseeding is intentionally a local script operation, not a public API route.

Season 0.x daily rollover:

```powershell
.\scripts\Register-ExpeditionHQSeasonReset.ps1
.\scripts\Audit-ExpeditionHQSeasonReset.ps1
```

Windows Task Scheduler is the source of truth for the daily 6am reset. Codex/OpenClaw automation should only run the audit script and report status; it should not register, unregister, start, or invoke the reset with `-Apply` unless August explicitly asks for a manual repair.

The rollover only updates ignored local season state under `data/`; it does not delete, rewrite, relock, or reclassify achievements, milestones, expedition records, field reports, event ledger records, or archive records. The dashboard reads `/season-current` for the active 6am-to-6am window and keeps `/season-summaries` available for history.
