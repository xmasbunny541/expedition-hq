import type { Agent, Event } from "../types";
import { displayName, stateLabel, VisualToken } from "./VisualToken";

export function CurrentActivity({
  agents,
  latestEventForAgent
}: {
  agents: Agent[];
  latestEventForAgent: (agent: Agent) => Event | undefined;
}) {
  const activityAgents = agents
    .filter((agent) => agent.allowed_as_little_guy || ["openclaw-to-codex-watcher", "chatgpt-openclaw-bridge", "openclaw-gateway"].includes(agent.id))
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
                <span>{stateLabel[agent.ui_state] ?? agent.ui_state}</span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
