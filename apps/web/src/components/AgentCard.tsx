import type { Agent, Event } from "../types";

const stateLabel: Record<string, string> = {
  awake: "Awake",
  on_call: "On Call",
  dormant: "Dormant",
  blocked: "Blocked",
  test_mode: "Test Mode",
  temporary_route: "Temporary Route",
  fragile_link: "Fragile Link",
  blueprint: "Blueprint",
  sleeping: "Sleeping",
  stable: "Stable",
  working_local: "Working Local"
};

const visualClassLabel: Record<string, string> = {
  specialist: "SP",
  candidate_specialist: "CS",
  automation: "AU",
  construct: "CT",
  route_bridge: "RT",
  interface: "UI",
  station: "ST",
  archive: "AR",
  data_source: "DS"
};

function formatXp(value = 0) {
  return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
}

function labelKey(value: string) {
  return value.replace(/_/g, " ");
}

function leadingClaimStatus(agent: Agent) {
  const counts = agent.xp_status?.claim_status_counts ?? {};
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  return entries[0]?.[0] ?? "no_claims";
}

export function AgentCard({ agent, latestEvent }: { agent: Agent; latestEvent?: Event }) {
  const xpStatus = agent.xp_status;
  const claimStatus = leadingClaimStatus(agent);
  return (
    <article className={`card agent state-${agent.ui_state}`}>
      <div className={`agent-avatar visual-${agent.visual_class}`} title={agent.visual_class}>
        <span>{visualClassLabel[agent.visual_class] ?? "HQ"}</span>
      </div>
      <div>
        <div className="agent-title-row">
          <h3>{agent.visual_name || agent.display_name}</h3>
          <strong className="agent-xp-badge">{formatXp(xpStatus?.awarded_xp ?? 0)} XP</strong>
        </div>
        <p className="muted code-line">{agent.id}</p>
        <dl className="agent-facts">
          <div>
            <dt>State</dt>
            <dd>{stateLabel[agent.ui_state] ?? agent.ui_state}</dd>
          </div>
          <div>
            <dt>Assignment</dt>
            <dd>{agent.current_assignment ?? "unassigned"}</dd>
          </div>
          <div>
            <dt>Latest</dt>
            <dd>{latestEvent ? latestEvent.title : "No event recorded"}</dd>
          </div>
          <div>
            <dt>XP state</dt>
            <dd>{labelKey(claimStatus)}</dd>
          </div>
          <div>
            <dt>Review</dt>
            <dd>{xpStatus?.review_item_count ?? 0} claim flags</dd>
          </div>
        </dl>
        <p>{agent.summary ?? "No summary recorded."}</p>
        <div className="pill-row">
          <span className="pill">{stateLabel[agent.ui_state] ?? agent.ui_state}</span>
          <span className="pill">events: {xpStatus?.event_count ?? 0}</span>
          <span className={xpStatus?.review_item_count ? "pill attention" : "pill"}>{labelKey(claimStatus)}</span>
          {agent.visual_archetype && <span className="pill">{agent.visual_archetype}</span>}
          {agent.room && <span className="pill">{agent.room}</span>}
        </div>
      </div>
    </article>
  );
}
