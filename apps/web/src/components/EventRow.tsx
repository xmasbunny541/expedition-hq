import type { Event } from "../types";

export function EventRow({ event }: { event: Event }) {
  const timestamp = new Date(event.timestamp);
  const displayTime = Number.isNaN(timestamp.valueOf())
    ? event.timestamp
    : timestamp.toLocaleString();
  const xp = (event.awarded_xp ?? event.xp).toLocaleString(undefined, { maximumFractionDigits: 1 });

  return (
    <li className={`event event-${event.status}`}>
      <div>
        <strong>{event.title}</strong>
        <p>{event.summary}</p>
        <div className="pill-row">
          <span className="pill">{event.event_type}</span>
          <span className="pill">risk: {event.risk_level}</span>
          {event.needs_review && <span className="pill attention">review</span>}
        </div>
      </div>
      <div className="event-meta">
        <span>{event.source_id}</span>
        <span>{displayTime}</span>
        <span>{xp} XP</span>
      </div>
    </li>
  );
}
