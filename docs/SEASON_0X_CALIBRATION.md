# Season 0.x Calibration

Season 0.x is a calibration window for Expedition HQ XP. The control set is intentionally stable.

## XP control rules

- `active_minutes` is the source of truth.
- `base_xp = active_minutes / 60`.
- `awarded_xp = base_xp * total_multiplier_raw`.
- The six scoring multipliers are grinding, party size, artifact, blocker break, reuse leverage, and risk control.
- Party size caps at `1.5`.
- Total multiplier is uncapped.
- Shadow multipliers are metadata only and do not affect XP.
- Formula changes should not happen during the test window unless August explicitly requests them.

## Proposal soft wagers

Proposal Desk wagers are simulated in Season 0.x.

- Approved proposals become eligible for implementation planning only.
- Denied proposals record `simulated_xp_loss` equal to the requested wager.
- Revised and deferred proposals record no simulated XP loss.
- Future accepted implementations may record `simulated_xp_gain` equal to the requested wager.
- Soft wager values never feed `base_xp`, `awarded_xp`, season summaries, or milestone XP.
- QA-only proposals may exist to exercise decision paths. They should be labeled clearly and excluded from normal reputation interpretation.

## Record preservation

XP resets are display/current-season resets. Event logs, proposal records, proposal decision events, and season summaries are preserved so Season 0.1, 0.2, 0.3, and later windows can be compared.

## Safety posture

Expedition HQ remains local-first. The Proposal Desk may write proposal records and proposal decision events to local SQLite only. It must not mutate OpenClaw, tunnels, tokens, memory stores, external systems, or production MCP.
