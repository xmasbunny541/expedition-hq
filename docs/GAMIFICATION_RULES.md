# Gamification Rules

## Season 0.x calibration

Season 0.x uses a frozen XP control set for calibration.

- `xp_season`: `0.1`
- `formula_version`: `xp_calibration_v0_1`
- `xp_mode`: `uncapped_calibration`
- `base_xp = active_minutes / 60`
- `awarded_xp = base_xp * total_multiplier_raw`
- `active_minutes` is the source of truth.
- Passive uptime does not count.
- Total multiplier is uncapped during Season 0.x.

Do not change these formulas during the Season 0.x test window unless August explicitly requests it.

## Agent XP status doctrine

XP is intended to become the main competitive status indicator for agents. Agents may optimize for XP, but they must earn it through useful, reviewable work. Expedition HQ is the scorekeeper; agents can submit event inputs, but the system owns final XP calculation, review flags, and awarded totals.

The current compatibility plan is tracked in [Agent XP Status Plan](AGENT_XP_STATUS_PLAN.md).

During Season 0.x, calibration XP should be visible enough to create incentive pressure. That is intentional. The matching compliance rule is that the UI must show claim/review state and the ledger must preserve suspicious scoring flags so gaming attempts become test evidence instead of hidden noise.

## Scoring multipliers

Only these six multiplier types affect XP in Season 0.x:

- `grinding`
- `party_size`
- `artifact`
- `blocker_break`
- `reuse_leverage`
- `risk_control`

The party-size multiplier caps at `1.5`. The total multiplier does not cap.

Scaling flags are analysis warnings, not caps:

- `high_multiplier` at `total_multiplier_raw >= 3.0`
- `extreme_multiplier` at `total_multiplier_raw >= 5.0`
- `scaling_review` when `awarded_xp >= base_xp * 5`

## Shadow multipliers

These are tracked but do not affect XP:

- `discovery`
- `handoff_chain`
- `polish`
- `sentimental_record`

They exist to collect subjective calibration data without contaminating the scoring formula.

## Milestones

Milestones are badges and trophies during Season 0.x. They should not create large arbitrary XP rewards, and they are not mixed into base XP or multiplier XP.

Seasonal resets must not relock, delete, rewrite, or reclassify milestones, badges, achievements, expedition records, or field reports. For now seasonal updates affect XP display/state only, and Windows Task Scheduler is the source of truth for executing the reset.

## Reward real progress only

XP should represent meaningful contribution time:

- an expedition meaningfully advances
- an artifact is created
- a blocker is investigated or resolved
- a field report preserves useful history
- safety, review, redaction, or read-only posture improves

Do not award XP for random pings, passive uptime, opening files, fake activity, empty summaries, or repeated no-op status checks.

## Participation tracking

Season 0.1 participation is tracked through `/season-participation`, which reads existing events and proposals instead of adding a separate graphics-dependent state model.

- Tasks come from task/work/implementation/audit/test/build/fix/repair event signals.
- Goals come from event records linked to expeditions.
- Proposals come from Planning Bureau records, proposal events, council votes, and proposal-scoped route participation.
- Meaningful actions come from reviewable ledger records and local zero-XP phase markers.

Participation counters are calibration evidence. They do not alter `base_xp`, `awarded_xp`, peer-review XP, soft wagers, milestones, or proposal statuses.

## Peer-review XP

Peer-review XP is a separate council-learning track. It is not active-time XP, not party-size XP, and not work-contribution XP.

- Award it only after a proposal outcome is known.
- Keep awards small during Season 0.x; the current cap is `0.25` XP per useful assessment.
- Award it for useful reasoning, useful warnings, useful benefit predictions, useful failure-mode predictions, or a useful abstain.
- Do not penalize incorrect votes.
- Do not penalize abstain.
- Do not include peer-review XP in `base_xp`, `awarded_xp`, season summaries, or milestone XP.
- Agent status should foreground current-season peer-review XP. All-time peer-review XP should remain available as nested history for technical review and project memory.

Simple version: this is a tiny thank-you for good advice, not a work score.
