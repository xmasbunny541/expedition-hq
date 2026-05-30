# Expedition HQ Codex Memory

This folder is project-local working memory for Codex collaboration on Expedition HQ.

It is not the product memory store and it is not a live integration surface. The dashboard remains read-only unless a future task explicitly designs and gates controls. This folder exists so future agents can preserve useful lessons, decisions, failures, open questions, and handoff state without rereading the whole project history.

## Rules

- Use memory when it prevents repeated mistakes, preserves a meaningful decision, records a real failure pattern, or helps the next agent continue safely.
- Do not create memory busywork. Trivial one-off questions do not need log entries.
- Do not store secrets, credentials, raw private transcripts, `.env` contents, private keys, tunnel URLs, auth tokens, or secret-bearing config.
- Prefer short, scoped entries with source, date, impact, and next step.
- Treat current files, tests, and live command output as more authoritative than stale memory.

## Layout

- `MEMORY.md`: durable project rules and reusable lessons.
- `SESSION-STATE.md`: current handoff/status for the active workstream.
- `learnings/`: reusable lessons from project work.
- `decisions/`: durable decisions and tradeoffs.
- `errors/`: failure patterns and fixes.
- `corrections/`: user corrections or course changes.
- `proactive/`: suggested next steps that should not be forgotten.
- `handoffs/`: compact handoffs after larger work sessions.
- `script-manifest.yml`: approved local helper scripts for memory operations.

## Useful Commands

```powershell
.\scripts\Initialize-CodexMemory.ps1
.\scripts\Update-SessionState.ps1 -Task "Describe current task" -Status "in_progress" -Notes "Important handoff detail."
.\scripts\Add-LearningEntry.ps1 -Title "Useful lesson" -Body "What future agents should remember."
.\scripts\Test-MemoryRedaction.ps1
.\scripts\Get-MemoryStats.ps1
.\scripts\Review-Memory.ps1
```

