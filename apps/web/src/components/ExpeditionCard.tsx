import type { Agent, Event, Expedition } from "../types";
import { displayName, VisualToken } from "./VisualToken";

export function ExpeditionCard({
  expedition,
  agentById,
  latestEvent
}: {
  expedition: Expedition;
  agentById?: Map<string, Agent>;
  latestEvent?: Event;
}) {
  return (
    <article className={`card expedition expedition-${expedition.status}`}>
      <h3>{expedition.name}</h3>
      <p className="muted">{expedition.status}</p>
      <p>{expedition.summary}</p>
      <div className="progress" aria-label={`${expedition.progress_percent}% complete`}>
        <div style={{ width: `${expedition.progress_percent}%` }} />
      </div>
      <p><strong>Next:</strong> {expedition.next_objective}</p>
      {latestEvent && (
        <p className="muted"><strong>Latest report:</strong> {latestEvent.title}</p>
      )}
      <div className="assigned-agents">
        {expedition.assigned_specialists.length ? expedition.assigned_specialists.map((agentId) => {
          const agent = agentById?.get(agentId);
          return (
            <span className="occupant-chip" key={agentId}>
              <VisualToken agent={agent} label={agent ? undefined : "AI"} size="small" />
              <span>{agent ? displayName(agent) : agentId}</span>
            </span>
          );
        }) : <span className="occupant-chip muted">No assigned specialist yet</span>}
      </div>
    </article>
  );
}
