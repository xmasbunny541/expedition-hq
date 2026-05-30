# Proposal Council System

Season 0.x now treats proposals as expedition plans placed before a council of specialists. The council can advise, but it does not approve work by itself and it never starts implementation.

Simple version for a 10 year old: one specialist suggests a plan. The plan is shown to other specialists. Each one can say "I support it," "I oppose it," or "I do not know enough." Saying "I do not know enough" is good behavior when the specialist would otherwise be guessing.

## Local flow

1. An agent or local script submits a proposal through `POST /proposals`.
2. Expedition HQ marks it as broadcasted and lists eligible reviewing specialists.
3. Eligible specialists may record votes through `POST /proposals/{proposal_id}/votes`.
4. A vote must include confidence, reasoning, expected benefit, expected failure mode, and risk notes.
5. August may still record the local Planning Bureau decision: approve, deny, revise, or defer.
6. The decision writes a local event ledger record only.
7. Approved proposals may be moved into the Work Queue with the Queue Work action. The stored status is still `in_progress`.
8. Queue Work records local state and a zero-XP ledger event only.
9. Implement Proposal moves a queued proposal into Actual Work. It authorizes proposal-scoped OpenClaw routing and creates a local Markdown implementation brief plus a provider-agnostic route snapshot.
10. Expedition HQ stays observability-first: it records OpenClaw's selected agents, candidate providers, skips, token-saving choices, evidence, and outcome without becoming the provider registry.
11. After work is done, the proposal should be marked implemented with evidence refs. Implemented is not Completed.
12. August is the final reviewer. Only final acceptance moves the proposal to Completed and records the simulated proposal-wager gain.

## Vote meanings

- `support`: "This plan looks worth trying."
- `oppose`: "This plan looks unwise or unsafe."
- `abstain`: "I do not know enough to make a useful call."

Abstain is not a failure. It is a clean record of uncertainty. A weak confident vote is worse than a clear abstain.

## Peer-review XP

Peer-review XP is separate from active-time XP, party-size XP, multiplier XP, milestone XP, and soft wager values.

- It records whether a review assessment later proved useful.
- It is small by design: at most `0.25` XP per useful assessment during this calibration pass.
- It is awarded only after the proposal outcome is known.
- Incorrect votes are not penalized.
- Abstain can be useful evidence, especially when the agent lacked context or had low confidence.
- Peer-review XP does not enter `base_xp`, `awarded_xp`, season summaries, or work-contribution leaderboards.

## Soft wager behavior

The original soft wager remains calibration metadata.

- Approve: proposal status becomes `approved`; no simulated XP loss is recorded.
- Queue Work: approved proposal status becomes `in_progress`; no real XP is recorded and no implementation automation is launched.
- Implement Proposal: queued proposal status becomes `implementation_requested`; a local implementation brief, dispatch job, and provider-agnostic OpenClaw route snapshot are recorded.
- Mark Implemented: implementation-requested proposal status becomes `implemented`; it waits for final review and records no real XP.
- Accept Implementation: implemented proposal status becomes `accepted`; simulated proposal-wager gain may be recorded.
- Reject Implementation: implemented proposal status becomes `rejected`; no simulated gain is recorded.
- Deny: proposal status becomes `denied`; `simulated_xp_loss` equals `requested_xp_wager`.
- Revise: proposal status becomes `revise_requested`; no simulated XP loss is recorded.
- Defer: proposal status becomes `deferred`; no simulated XP loss is recorded.
- Accepted implementation later: future status may record `simulated_xp_gain` equal to `requested_xp_wager`.

## Candidate visiting specialists

External systems such as Copilot, Claude, Perplexity, Gemini, DeepSeek, Kimi, and Manus can appear as candidate visiting specialists. They are not trusted HQ agents by default.

They start as unprofiled candidates. Their free-tier capabilities can be tested with redacted prompts and local records. If they produce useful, safe council assessments over time, they can be promoted later. If they are only useful for narrow low-risk checks, they can remain minimum-wage candidates.

## Candidate promotion

Candidate providers move through a simple trust ladder: `unprofiled_candidate`, `profiled_candidate`, `trusted_reviewer`, `limited_implementer`, and `trusted_implementer`.

Promotion is not a constant August triage task. Expedition HQ records evidence continuously, then surfaces concise promotion dossiers at season rollover and, for longer seasons, near the season midpoint. A dossier should show pros, cons, recommendation, next gate, and evidence. Agents cannot self-promote; trust changes require explicit local promotion events.

## Guardrails

- Expedition HQ does not store provider credentials or manage free-tier account setup.
- No external candidate receives secrets or raw transcripts.
- No vote is treated as an implementation command.
- Queue Work is a local planning marker, not an agent launch command.
- Implement Proposal is the proposal-scoped authorization point; OpenClaw owns provider routing while Expedition HQ records the route and evidence trail.
- No peer-review XP is mixed into work XP.
- Proposal records must stay local and reviewable.
