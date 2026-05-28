import type { Expedition } from "../types";

export function ExpeditionCard({ expedition }: { expedition: Expedition }) {
  return (
    <article className={`card expedition expedition-${expedition.status}`}>
      <h3>{expedition.name}</h3>
      <p className="muted">{expedition.status}</p>
      <p>{expedition.summary}</p>
      <div className="progress" aria-label={`${expedition.progress_percent}% complete`}>
        <div style={{ width: `${expedition.progress_percent}%` }} />
      </div>
      <p><strong>Next:</strong> {expedition.next_objective}</p>
      <p className="muted">Assigned: {expedition.assigned_specialists.length ? expedition.assigned_specialists.join(", ") : "none yet"}</p>
    </article>
  );
}
