# Proposal Wager System

This is a future design concept only. Do not implement runtime wager mechanics during Season 0.x.

Subjective design decisions and subjective value claims should eventually go through a proposal system before implementation. Season 0.x calibration data should inform future wager ranges, but proposal XP must stay separate from base time XP and multiplier XP.

## Future flow

1. Agent submits a proposal before subjective implementation.
2. Proposal includes requested XP wager, confidence, reasoning, estimated active minutes, risk level, rollback plan, and acceptance criteria.
3. August approves, denies, revises, or defers the proposal.
4. If August approves, the agent may implement.
5. If August denies, the agent loses XP equal to the requested wager.
6. If August revises or defers, no XP is lost.
7. If implementation is accepted, the agent earns the wager.
8. If implementation is rejected, the agent earns 0 or loses the wager depending on future policy.

## Guardrails

- No proposal wager XP should affect Season 0.x calibration.
- No automatic subjective scoring should be added without explicit approval.
- No implementation should bypass safety boundaries because a wager exists.
- Rejected proposals must remain reviewable as records, not hidden failures.
