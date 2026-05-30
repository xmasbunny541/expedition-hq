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

## Planning Bureau soft wagers

Planning Bureau wagers are simulated in Season 0.x.

- Approved proposals become eligible for implementation planning only.
- A local Queue Work action may move approved proposals into the Work Queue, store status as `in_progress`, and record a zero-XP `proposal_work_started` event.
- A local Implement Proposal action may move queued proposals into Actual Work, store status as `implementation_requested`, and create a Markdown implementation brief, dispatch job, and provider-agnostic OpenClaw route snapshot.
- Expedition HQ observes the implementation route rather than owning the provider registry. OpenClaw can route enabled providers for cross-reference or implementation support; HQ records selected agents, candidate providers, skipped providers, token-saving choices, evidence, and outcomes.
- Implemented work waits in Final Review until August accepts or rejects it. Only accepted implementation outcomes move to Completed.
- Denied proposals record `simulated_xp_loss` equal to the requested wager.
- Revised and deferred proposals record no simulated XP loss.
- Future accepted implementations may record `simulated_xp_gain` equal to the requested wager.
- Soft wager values never feed `base_xp`, `awarded_xp`, season summaries, or milestone XP.
- QA-only proposals may exist to exercise decision paths. They should be labeled clearly and excluded from normal reputation interpretation.

## Specialist council reviews

Proposals are also broadcast to eligible specialists for local peer review.

- Vote options are `support`, `oppose`, and `abstain`.
- Each vote records confidence, simple reasoning, expected benefit, expected failure mode, and risk notes.
- Abstain is healthy when the specialist lacks context or has low confidence.
- Peer-review XP is a separate learning track and does not affect active-time XP, party-size XP, season summaries, or milestone XP.
- No incorrect vote creates a penalty.
- Current-season peer-review XP should be shown first in agent status and council analytics. All-time peer-review XP should remain nested for later technical and sentimental review.

## Candidate promotion cadence

Untested providers and new agents start as candidates. They can contribute redacted review, cross-reference, scouting, or critique before they become trusted implementers.

Promotion reviews should be seasonal, not a constant August inbox. HQ records evidence continuously and surfaces concise promotion dossiers at season rollover. Longer seasons may also show a midpoint review. Daily Season 0.x windows should skip noisy midpoint reviews.

## Record preservation

XP resets are display/current-season XP resets only. They may update the active XP window and `data/season-state.json`; they must not delete, rewrite, relock, or reclassify achievements, milestones, badges, expedition records, event logs, field reports, proposal records, proposal decision events, artifacts, routes, rooms, agent roster records, or season summaries.

Season 0.1, 0.2, 0.3, and later windows must stay comparable because the underlying records remain intact.

## Daily season windows

May 29, 2026 is a warm-up calibration day because too little XP was tracked to justify starting the daily seasonal tempo. Season 0.1 starts fresh at the May 30, 2026 6am local window. After that, Season 0.x advances one decimal step each day at 6am: 0.2, 0.3, 0.4, and so on.

The active dashboard totals use the current 6am-to-6am window. The event ledger remains append-only, expedition records remain durable, achievement-style records remain durable, and historical summaries remain available for comparison.

## Scheduler authority

Windows Task Scheduler is the source of truth for daily Season 0.x reset execution. Codex/OpenClaw automation may audit and report scheduler state, next run time, last result, and current season preview, but it must not independently perform seasonal resets.

The local policy lives in `config/season-policy.seed.json`. Register the Task Scheduler entry manually with:

```powershell
.\scripts\Register-ExpeditionHQSeasonReset.ps1
```

Use the audit helper for Codex/reporting automation:

```powershell
.\scripts\Audit-ExpeditionHQSeasonReset.ps1
```

The lower-level rollover command with `-Apply` is the scheduled task action and a manual repair/backfill tool, not the Codex automation path.

## Safety posture

Expedition HQ remains local-first and observability-first. The Planning Bureau may write proposal records, dispatch jobs, route snapshots, and proposal decision events to local SQLite/runtime files. It does not store provider credentials or manage free-tier account setup.
