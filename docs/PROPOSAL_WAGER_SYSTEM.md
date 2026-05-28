# Proposal Wager System

Season 0.x includes a local Proposal Desk MVP. It records subjective or directional proposals and soft wager decisions in Expedition HQ SQLite only.

The current wager is simulated. It does not change `base_xp`, `awarded_xp`, season summaries, milestone rewards, or any agent reputation score.

## MVP flow

1. Agent or script submits a proposal through `POST /proposals`.
2. Proposal includes requested XP wager, confidence, reasoning, estimated active minutes, risk level, affected areas, acceptance criteria, and rollback plan.
3. August reviews the proposal in the Proposal Desk.
4. A local decision can approve, deny, revise, or defer the proposal.
5. The decision writes a `proposal_decision` event to the local event ledger.
6. Approved proposals become eligible for implementation planning only.
7. No proposal decision triggers implementation or any external action.

## Season 0.x decision behavior

- Approve: proposal status becomes `approved`; no simulated XP loss is recorded.
- Deny: proposal status becomes `denied`; `simulated_xp_loss` equals `requested_xp_wager`.
- Revise: proposal status becomes `revise_requested`; no simulated XP loss is recorded.
- Defer: proposal status becomes `deferred`; no simulated XP loss is recorded.
- Accepted implementation later: future status may record `simulated_xp_gain` equal to `requested_xp_wager`.

## Future rules to evaluate

- Proposal wager XP should remain separate from base time XP and multiplier XP.
- Accepted implementations may earn the requested wager.
- Rejected implementations may earn zero or lose the wager, depending on a future policy decision.
- Season 0.x calibration data should inform reasonable wager ranges.

## Guardrails

- No proposal wager XP affects Season 0.x calibration.
- No automatic subjective scoring is active.
- No implementation starts because a proposal was approved.
- No OpenClaw, tunnel, token, memory store, external system, or production MCP mutation is allowed.
- Rejected or denied proposals remain reviewable records.
