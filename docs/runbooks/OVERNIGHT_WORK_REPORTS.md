# Overnight Work Reports

Hourly overnight Expedition HQ work reports should be written under:

```text
runtime/overnight-reports/2026-05-28-to-2026-05-29/
```

Use `INDEX.md` as the first morning review file. Each hourly report should include:

- local start and end time
- task chosen and why it was the next safest useful step
- files touched
- verification run and result
- blockers or risks
- next recommended step

These reports are local runtime artifacts. They are not source-controlled and should not contain secrets, tokens, raw transcripts, tunnel material, or unredacted private artifacts.

## Verification Commands

In PowerShell, prefer `npm.cmd` for routine overnight verification. Plain `npm` may resolve to `npm.ps1` and fail when script execution is disabled on the workstation.

```powershell
npm.cmd run seed:validate
npm.cmd run api:test
npm.cmd run web:build
```

## Season Reset Boundary

Windows Task Scheduler is the source of truth for Expedition HQ seasonal resets. Overnight Codex automation may run `scripts\Audit-ExpeditionHQSeasonReset.ps1` and summarize its JSON output, but it must not register, unregister, start, or invoke the scheduled reset. It must not run `scripts\Invoke-ExpeditionHQSeasonRollover.ps1 -Apply` unless August explicitly asks for a manual repair in the active conversation.

Seasonal reset reporting should confirm that resets affect only XP display/state. Achievements, milestones, badges, expedition records, field reports, events, artifacts, routes, rooms, agent roster records, proposals, and season summaries remain preserved records.
