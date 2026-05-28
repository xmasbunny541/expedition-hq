import type { Agent, Event, Incident } from "../types";
import { displayName, VisualToken } from "./VisualToken";

export function ReviewDesk({
  events,
  incidents,
  agentById
}: {
  events: Event[];
  incidents: Incident[];
  agentById: Map<string, Agent>;
}) {
  const reviewEvents = events
    .filter((event) => event.needs_review || ["medium", "high"].includes(event.risk_level) || event.status === "blocked")
    .slice(0, 4);
  const blockedIncidents = incidents.filter((incident) => incident.status === "open").slice(0, 3);

  return (
    <section className="panel review-panel">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">Review Desk</p>
          <h2>Items Needing Eyes</h2>
        </div>
        <span className="review-count">{reviewEvents.length + blockedIncidents.length}</span>
      </div>

      <div className="review-list">
        {reviewEvents.map((event) => {
          const agent = agentById.get(event.source_id);
          return (
            <article className="review-item" key={event.id}>
              <VisualToken agent={agent} label={agent ? undefined : "EV"} size="small" />
              <div>
                <h3>{event.title}</h3>
                <p>{agent ? displayName(agent) : event.source_id}</p>
              </div>
              <span className={`badge risk-${event.risk_level}`}>{event.risk_level}</span>
            </article>
          );
        })}
        {blockedIncidents.map((incident) => (
          <article className="review-item" key={incident.id}>
            <VisualToken label="IN" kind="system" size="small" state="blocked" />
            <div>
              <h3>{incident.summary}</h3>
              {incident.impact && <p>{incident.impact}</p>}
            </div>
            <span className="badge risk-high">blocked</span>
          </article>
        ))}
        {!reviewEvents.length && !blockedIncidents.length && (
          <p className="empty compact-empty">No review items in the local ledger.</p>
        )}
      </div>
    </section>
  );
}
