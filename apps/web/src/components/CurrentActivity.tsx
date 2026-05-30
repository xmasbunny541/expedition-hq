import type { Agent, Event } from "../types";
import { displayName, stateLabel, VisualToken } from "./VisualToken";

export function CurrentActivity({
  agents,
  latestEventForAgent
}: {
  agents: Agent[];
  latestEventForAgent: (agent: Agent) => Event | undefined;
}) {
  const statePriority: Record<string, number> = {
    blocked: 0,
    awake: 1,
    on_call: 2,
    test_mode: 3,
    temporary_route: 4,
    working_local: 5,
    dormant: 6,
    sleeping: 7,
    blueprint: 8
  };
  const activityAgents = [...agents]
    .filter((agent) => agent.allowed_as_little_guy || ["awake", "on_call", "blocked", "test_mode", "temporary_route"].includes(agent.ui_state))
    .sort((a, b) => {
      const stateDelta = (statePriority[a.ui_state] ?? 99) - (statePriority[b.ui_state] ?? 99);
      if (stateDelta !== 0) return stateDelta;
      return (b.last_observed_at ?? "").localeCompare(a.last_observed_at ?? "");
    })
    .slice(0, 7);

  return (
    <section className="panel activity-panel">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">Latest Signals</p>
          <h2>Current Activity</h2>
        </div>
      </div>
      <div className="activity-list">
        {activityAgents.map((agent) => {
          const event = latestEventForAgent(agent);
          return (
            <article className="activity-item" key={agent.id}>
              <VisualToken agent={agent} />
              <div>
                <h3>{displayName(agent)}</h3>
                <p>{event?.title ?? "No event recorded"}</p>
                <span>{stateLabel[agent.ui_state] ?? agent.ui_state} / {agent.room?.replace(/-/g, " ") ?? "unassigned"}</span>
                {event?.summary && <p className="activity-reason">{event.summary}</p>}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
