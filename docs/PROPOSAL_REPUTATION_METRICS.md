# Proposal Reputation Metrics

This is planning documentation only. Expedition HQ should not compute or apply proposal reputation during Season 0.x.

Future reputation metrics should help compare proposal quality without turning subjective design taste into automatic XP.

## Candidate metrics

- Approval rate: share of proposals August approves.
- Revision rate: share of proposals August revises before approval.
- Denial rate: share of proposals August denies.
- Accepted implementation rate: share of approved proposals whose implementation is accepted.
- Rollback rate: share of accepted proposals that later need rollback.
- Estimate accuracy: actual active minutes compared with proposed active minutes.
- Risk accuracy: observed risk compared with proposed risk level.
- Wager calibration: requested wager compared with accepted value and actual active effort.

## Use in later seasons

Season 0.x data should be used to choose reasonable wager ranges and identify overconfident proposal patterns. Proposal reputation should stay advisory until August explicitly approves a scoring policy.

## Guardrails

- Keep proposal reputation separate from active-time XP and multiplier XP.
- Preserve proposal records even when XP resets.
- Do not punish revised or deferred proposals.
- Do not let subjective polish tags automatically inflate awarded XP.
