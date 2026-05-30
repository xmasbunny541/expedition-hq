# Write Field Report

Given a completed task, create a field report JSON file under `archive/field-reports/`.

Include:
- timestamp
- expedition_id
- source_id
- title
- summary
- changed_files
- artifact_refs
- risk_level
- needs_review
- sentimental_note
- active_minutes
- evidence_refs
- scoring_multipliers
- shadow_multipliers

The API computes final XP. Do not invent `base_xp`, `awarded_xp`, or `total_multiplier_raw`.

Keep it factual. Do not invent success.
