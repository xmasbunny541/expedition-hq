# Expedition HQ Project Memory

## Status

- Project-local Codex memory was initialized for `C:\Users\augus\Desktop\expedition-hq` on 2026-05-29.
- This memory is for development collaboration only. It does not change Expedition HQ's product stance as a read-only observability dashboard.

## Durable Rules

- Keep Expedition HQ local-first and read-only for the MVP.
- Do not use the product to mutate external memory stores, OpenClaw config, tunnel state, tokens, or production MCP setup.
- Store neutral operational data and render it through the Expedition HQ theme.
- Prefer environmental state, room placement, routes, artifacts, and activity trails over another card grid or scoreboard.
- Avoid fake agent autonomy. Visual state must reflect seed data or real events.
- Every time Expedition HQ adds a new dashboard screen, run a visual smoke pass before calling it done. This gives fast feedback on the human-facing layer without pretending it proves the whole system is correct.

## Memory Hygiene

- Add memory only when it prevents repeated mistakes, preserves a meaningful decision, captures a real failure pattern, or helps the next agent continue safely.
- Keep entries short and scoped.
- Do not store secrets, credentials, raw private transcripts, `.env` contents, private keys, tunnel URLs, auth tokens, or secret-bearing config.
- If memory conflicts with current repo files, explicit user instructions, or live command output, use current evidence and update memory only when explicitly requested or clearly part of the task.

