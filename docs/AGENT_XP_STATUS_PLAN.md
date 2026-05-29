# Agent XP Status Plan

## Goal

Make XP the main competitive status indicator for agents without letting agents self-award status.

The rule is simple: agents may chase XP, but Expedition HQ is the scorekeeper. Agents submit useful, reviewable work records; Expedition HQ decides what earns XP.

Season 0.x is a calibration and stress-test window. XP should be visible enough to create real optimization pressure, because that pressure reveals how agents try to game the ledger before the score matters as durable reputation.

## 10-point action plan

1. **Make calibration XP visible as agent status**
   Show awarded XP beside every agent wherever status appears during Season 0.x. Label it as calibration XP, not final reputation, so August can watch incentives form before the score becomes durable.

2. **Accept work from any project**
   Keep Expedition HQ project-neutral. Work outside this repo can earn XP when it is recorded as an event with a clear `source_id`, `expedition_id`, summary, active minutes, and evidence.

3. **Separate claims from awards**
   Agents should submit XP claims. Expedition HQ should normalize, flag, and label those claims before display. During Season 0.x, suspicious claims should stay visible as stress-test data rather than being silently suppressed.

4. **Require evidence for nonzero XP**
   A nonzero-XP event should point to something reviewable: an artifact path, field report, issue, test output, command result, decision record, or redacted summary. Missing evidence should create a review flag during Season 0.x.

5. **Reward useful work only**
   Award XP for completed work, useful investigation, artifact creation, blocker progress, safety improvement, or durable handoff. Do not award XP for passive uptime, chatter, empty summaries, repeated no-op checks, or fake activity.

6. **Flag suspicious scoring**
   Events with high multipliers, large active-minute claims, missing evidence, unknown agents, duplicate summaries, weak summaries, oversized party credit, or repeated tiny submissions should be marked for review. These flags are part of the stress-test output.

7. **Keep the formula centralized**
   Agents should not choose final `base_xp`, `awarded_xp`, or `total_multiplier_raw`. They can propose inputs; the API should compute the final score from the active season formula.

8. **Attribute team work fairly**
   Split credit across `source_id` and verified `party_agents`. Party credit should represent real collaboration, not a free multiplier an agent can add to inflate XP.

9. **Keep soft status separate from real XP**
   Proposals, sentiment, polish, discovery, and badges can be displayed, but they should not silently alter real XP. Shadow multipliers and simulated wagers stay advisory until a later policy explicitly promotes them.

10. **Preserve audit history across seasons**
    Resets should affect the current-season display, not the underlying ledger. Keep events, field reports, season summaries, review decisions, rejected claims, and gaming-pattern flags so future XP rules can be compared honestly.

## Implementation order

1. Add an `xp_claim_status` field to distinguish clean calibration awards from review-pending claims.
2. Add evidence fields for nonzero-XP event ingestion and flag missing evidence.
3. Add review flags for suspicious XP patterns.
4. Show per-agent awarded XP prominently in the dashboard with claim/review state beside it.
5. Add a cross-project event helper so outside work is easy to log with evidence.
6. Add tests that prove agents cannot provide final awarded XP directly.

## Devil's-advocate check

The danger is incentive rot: if XP becomes the top status signal, agents will optimize for it. In Season 0.x, that is useful only if the scoreboard also exposes the audit trail of how agents try to optimize it. If the easiest path becomes noisy event spam or inflated time claims and the system does not record that behavior, the test produces noise instead of calibration data.

The current Season 0.x formula is a good calibration base, but it is still closer to a structured honor ledger than hard telemetry. The next compatibility step is not a fancier multiplier; it is visible calibration XP plus stricter claim review and easier cross-project logging.
