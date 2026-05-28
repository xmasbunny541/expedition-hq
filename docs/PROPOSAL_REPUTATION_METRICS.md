# Proposal Reputation Metrics

Proposal reputation remains advisory during Season 0.x. Expedition HQ may display local proposal analytics, but it must not compute or apply real reputation, XP rewards, or XP penalties from proposals yet.

## MVP analytics

The Proposal Desk currently shows:

- Proposal count by type.
- Approval, denial, defer, revise, and status counts.
- Average requested wager.
- Average confidence.
- Simulated XP at risk for pending proposals.
- Simulated XP lost for denied proposals.
- Proposal count by source agent.
- QA-only denial probes are labeled separately and excluded from normal proposal reputation analytics.

These metrics help August evaluate proposal quality and calibration pressure. They are not a scoring policy.

## Candidate future metrics

- Approval rate: share of proposals August approves.
- Revision rate: share of proposals August revises before approval.
- Denial rate: share of proposals August denies.
- Accepted implementation rate: share of approved proposals whose implementation is accepted.
- Rollback rate: share of accepted proposals that later need rollback.
- Estimate accuracy: actual active minutes compared with proposed active minutes.
- Risk accuracy: observed risk compared with proposed risk level.
- Wager calibration: requested wager compared with accepted value and actual active effort.

## Guardrails

- Keep proposal reputation separate from active-time XP and multiplier XP.
- Preserve proposal records even when XP resets.
- Do not punish revised or deferred proposals during Season 0.x.
- Do not let subjective polish, discovery, handoff, or sentimental tags automatically inflate awarded XP.
- Do not use proposal analytics as an implementation queue or external automation trigger.
- Do not treat deliberately bad QA proposals as product direction or agent reputation evidence.
