import type { Agent, Event } from "../types";
import { displayName, VisualToken } from "./VisualToken";

function displayTime(value: string) {
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.valueOf()) ? value : timestamp.toLocaleString();
}

function formatXp(value = 0) {
  return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
}

function formatMultiplier(value = 1) {
  return `${Number(value).toFixed(2).replace(/\.?0+$/, "")}x`;
}

function labelKey(value: string) {
  return value.replace(/_/g, " ");
}

export function FieldReportCard({
  event,
  source
}: {
  event: Event;
  source?: Agent;
}) {
  const scoringEntries = Object.entries(event.scoring_multipliers ?? {});
  const shadowTags = Object.entries(event.shadow_multipliers ?? {})
    .filter(([, enabled]) => enabled)
    .map(([key]) => key);
  const reviewFlags = (event.review_flags ?? []).filter((flag) => !(event.scaling_flags ?? []).includes(flag));

  return (
    <article className={`field-report report-${event.status}`}>
      {source ? <VisualToken agent={source} /> : <VisualToken label="FR" kind="report" />}
      <div>
        <header className="field-report-header">
          <div>
            <p className="eyebrow">{source ? displayName(source) : event.source_id}</p>
            <h3>{event.title}</h3>
          </div>
          <strong>{formatXp(event.awarded_xp ?? event.xp)} XP</strong>
        </header>
        <p>{event.summary}</p>
        <div className="xp-breakdown">
          <div><span>active</span><strong>{event.active_minutes ?? 0}m</strong></div>
          <div><span>base</span><strong>{formatXp(event.base_xp)} XP</strong></div>
          <div><span>awarded</span><strong>{formatXp(event.awarded_xp ?? event.xp)} XP</strong></div>
          <div><span>total</span><strong>{formatMultiplier(event.total_multiplier_raw)}</strong></div>
        </div>
        {scoringEntries.length > 0 && (
          <div className="multiplier-grid" aria-label="XP multiplier breakdown">
            {scoringEntries.map(([key, value]) => (
              <span key={key}>{labelKey(key)} <strong>{formatMultiplier(value)}</strong></span>
            ))}
          </div>
        )}
        <div className="pill-row">
          <span className="pill">{event.event_type}</span>
          <span className={`pill ${event.xp_claim_status === "review_pending" ? "attention" : ""}`}>
            {labelKey(event.xp_claim_status ?? "calibration_awarded")}
          </span>
          <span className={`pill risk-${event.risk_level}`}>risk: {event.risk_level}</span>
          <span className="pill">party: {event.party_size ?? 0}</span>
          {event.evidence_refs?.length > 0 && <span className="pill">evidence: {event.evidence_refs.length}</span>}
          {event.artifact_refs?.length > 0 && <span className="pill">artifacts: {event.artifact_refs.length}</span>}
          {event.party_agents?.length > 0 && <span className="pill">agents: {event.party_agents.join(", ")}</span>}
          {event.needs_review && <span className="pill attention">review</span>}
          {event.scaling_flags?.map((flag) => <span className="pill attention" key={flag}>{labelKey(flag)}</span>)}
          {reviewFlags.map((flag) => <span className="pill attention" key={flag}>{labelKey(flag)}</span>)}
          {shadowTags.map((tag) => <span className="pill shadow" key={tag}>{labelKey(tag)}</span>)}
          <span className="pill">{displayTime(event.timestamp)}</span>
        </div>
      </div>
    </article>
  );
}
