# START HERE

## 1. Create a fresh Codex project

Copy this folder into your desired project location, for example:

```bash
cp -R expedition-hq-codex-starter ~/Projects/expedition-hq
cd ~/Projects/expedition-hq
git init
```

## 2. Make the first commit

```bash
git add .
git commit -m "Initialize Expedition HQ starter scaffold"
```

## 3. Give Codex the project prompt

Open `CODEX_PROJECT_PROMPT.md` and paste it into the fresh Codex project.

## 4. Initialize project memory

Expedition HQ includes project-local Codex memory in `.codex-memory/`. It is for lessons, decisions, errors, open questions, and handoffs. It is not a product memory-write feature.

```powershell
.\scripts\Initialize-CodexMemory.ps1
.\scripts\Test-MemoryRedaction.ps1
```

## 5. First implementation objective

Have Codex make the backend run from the seed files and the web app render:
- The Coordinator
- The Archivist
- The Dormant Engineer
- The Rover
- The Signal Mast
- The Checkpoint
- The Harbor Gate
- The Field Handset
- The Archive Vault
- The Map Room

## 6. Non-negotiable rule

First version is read-only. No tunnel control, no token rotation, no OpenClaw config mutation, no live external sends, and no memory mutation.

## 7. Local ports

- API: `http://127.0.0.1:8789`
- Web: `http://127.0.0.1:5173`

Use `python scripts/validate_seed.py` and `python scripts/init_db.py` before launching the API. If plain `python` is not available, install Python 3.11+ or activate the project virtual environment first.
