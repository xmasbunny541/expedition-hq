import type { Agent, Event } from "../types";
import { displayName, VisualToken } from "./VisualToken";

function displayTime(value: string) {
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.valueOf()) ? value : timestamp.toLocaleString();
}

export function FieldReportCard({
  event,
  source
}: {
  event: Event;
  source?: Agent;
}) {
  return (
    <article className={`field-report report-${event.status}`}>
      {source ? <VisualToken agent={source} /> : <VisualToken label="FR" kind="report" />}
      <div>
        <header className="field-report-header">
          <div>
            <p className="eyebrow">{source ? displayName(source) : event.source_id}</p>
            <h3>{event.title}</h3>
          </div>
          <strong>{event.xp} XP</strong>
        </header>
        <p>{event.summary}</p>
        <div className="pill-row">
          <span className="pill">{event.event_type}</span>
          <span className={`pill risk-${event.risk_level}`}>risk: {event.risk_level}</span>
          {event.needs_review && <span className="pill attention">review</span>}
          <span className="pill">{displayTime(event.timestamp)}</span>
        </div>
      </div>
    </article>
  );
}
