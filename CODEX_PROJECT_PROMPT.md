# Codex Project Prompt: Expedition HQ MVP

You are working inside the Expedition HQ starter repository.

## Goal

Build a local-first, read-only Expedition HQ dashboard for observing August's AI ecosystem. The dashboard should make it easy to visually answer:

> What are my little AI guys doing?

The app should represent agents and agent-like systems as visual specialists/constructs, represent multiple concurrent projects as expeditions, record progress through events/field reports/artifacts, and add light gamification through milestones and badges.

## Strict constraints

- Start read-only.
- Do not add controls that mutate OpenClaw, Cloudflare, Codex, tunnels, tokens, external messages, or memory stores.
- Do not commit secrets, live tunnel URLs, OAuth material, raw transcripts, or machine scheduler state.
- Use `config/*.seed.json` and `archive/artifacts/bootstrap/agent-census-2026-05-27.redacted.json` as seed data.
- Preserve origin notes and decisions inside the repo.
- Keep visual fun driven by real state, not fake busywork.

## First tasks

1. Inspect the repository.
2. Validate all JSON files with `python scripts/validate_seed.py`.
3. Implement the FastAPI app enough to serve:
   - `GET /health`
   - `GET /agents`
   - `GET /expeditions`
   - `GET /events`
   - `POST /events`
   - `GET /milestones`
   - `GET /incidents`
4. Create SQLite initialization from `db/migrations/001_initial.sql`.
5. Wire the React app to either seed JSON or the local API.
6. Render:
   - Bureau HQ
   - Expedition Board
   - Specialist Roster
   - Field Reports
   - Milestone Gallery
7. Add state-driven visual behavior:
   - awake
   - on_call
   - dormant
   - blocked
   - test_mode
   - temporary_route
8. Write a bootstrap field report when the app first runs or via a script.

## Definition of done for first pass

- App can run locally.
- Seed census produces a visible roster.
- At least three expeditions appear.
- At least five events appear in the Field Reports timeline.
- At least three visual states are obvious without opening logs.
- No secrets or live URLs are committed.
