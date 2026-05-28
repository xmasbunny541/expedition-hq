# AGENTS.md — Expedition HQ

## Mission

Build Expedition HQ as a local-first, read-only observability and archive system for August's AI ecosystem.

## Product intent

The dashboard should feel like a living Expedition HQ:
- agents appear as little specialists
- automations appear as constructs/towers/rovers
- routes appear as bridges/gates/portals
- memory stores appear as archives/vaults
- active workflows appear as expeditions
- events become field reports
- durable outputs become artifacts
- progress becomes milestones, XP, and badges

## Do not over-theme the data model

Store neutral operational data:
- agents
- expeditions
- events
- artifacts
- routes
- incidents
- milestones
- badges
- reviews

Render those through the Expedition HQ theme in the UI.

## Safety boundaries

Do not implement live control actions in the MVP:
- no tunnel start/stop
- no token rotation
- no OpenClaw config mutation
- no external sends
- no memory mutation
- no production MCP setup
- no raw transcript ingestion unless redacted
- no display of secret-bearing artifacts

## Development priorities

1. Validate seed data.
2. Build the event ledger.
3. Serve read-only API data.
4. Render useful dashboard screens.
5. Add field reports and milestones.
6. Add light animation/state hooks.
7. Add live integrations only after read-only MVP is stable.

## Coding rules

- Favor small, reviewable commits.
- Keep config examples redacted.
- Add tests when changing schemas or event ingestion.
- Prefer simple JSON/SQLite before adding complex dependencies.
- Avoid fake agent autonomy. Visual state must reflect seed data or real events.
