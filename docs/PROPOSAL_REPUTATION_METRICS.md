# Proposal Reputation Metrics

Proposal reputation remains advisory during Season 0.x. The council is a learning record, not a corporate approval workflow and not an implementation queue.

Simple version for a 10 year old: the HQ remembers which specialists gave helpful advice. It does not punish them for being wrong, because the point is to learn who gives useful warnings, who spots benefits, and who is honest enough to abstain.

## Current Planning Bureau metrics

- Proposal count by type.
- Proposal count by source agent.
- Approval, denial, defer, revise, and status counts.
- Support, oppose, and abstain vote counts.
- Eligible specialist count and participation count.
- Healthy abstain count.
- Average confidence by vote type.
- Average requested soft wager.
- Simulated XP at risk for pending proposals.
- Simulated XP lost for denied proposals.
- Separate peer-review XP awarded after useful assessments.
- QA-only denial probes are labeled separately and excluded from normal proposal reputation analytics.

## Useful assessment signals

A vote can be marked useful after the proposal outcome is known when it did one of these things:

- named a real benefit that later mattered
- named a failure mode that later appeared or was avoided
- flagged a safety risk that changed the plan
- abstained because the agent lacked enough context and avoided fake certainty
- gave reasoning simple enough for August to judge quickly

## Metrics to avoid

- Do not rank agents by support rate alone.
- Do not punish opposition when the plan later succeeds.
- Do not punish support when the plan later fails.
- Do not punish abstain.
- Do not mix peer-review XP with active-time XP.
- Do not treat visiting candidate votes as trusted-agent votes until they have a local profile.

## Candidate future metrics

- Review usefulness rate.
- Useful abstain rate.
- Risk-note usefulness.
- Benefit-prediction usefulness.
- Failure-mode prediction usefulness.
- Confidence calibration after outcomes are known.
- Candidate specialist promotion readiness.
- Minimum-wage candidate usefulness for narrow low-risk checks.

## Guardrails

- Keep proposal reputation separate from active-time XP and multiplier XP.
- Preserve proposal records even when XP resets.
- Do not let subjective polish, discovery, handoff, or sentimental tags automatically inflate awarded XP.
- Do not use proposal analytics as an implementation queue or external automation trigger.
- Do not treat deliberately bad QA proposals as product direction or agent reputation evidence.
