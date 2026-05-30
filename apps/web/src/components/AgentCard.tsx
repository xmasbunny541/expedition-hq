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

function displayTime(value?: string) {
  if (!value) return "not observed";
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.valueOf()) ? value : timestamp.toLocaleString();
}

function leadingClaimStatus(agent: Agent) {
  const counts = agent.xp_status?.claim_status_counts ?? {};
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  return entries[0]?.[0] ?? "no_claims";
}

export function AgentCard({ agent, latestEvent }: { agent: Agent; latestEvent?: Event }) {
  const xpStatus = agent.xp_status;
  const claimStatus = leadingClaimStatus(agent);
  const currentCouncilXp = xpStatus?.peer_review_xp ?? 0;
  const currentCouncilVotes = xpStatus?.peer_review_assessment_count ?? 0;
  const allTimeCouncil = xpStatus?.peer_review_all_time;
  const candidateProfile = agent.candidate_profile;
  const promotionDossier = candidateProfile?.promotion_dossier;
  const showAllTimeCouncil = Boolean(allTimeCouncil && (
    allTimeCouncil.peer_review_assessment_count !== currentCouncilVotes
    || allTimeCouncil.peer_review_xp !== currentCouncilXp
  ));
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
            <dd>{agent.latest_event_title ?? latestEvent?.title ?? "No event recorded"}</dd>
          </div>
          <div>
            <dt>Last seen</dt>
            <dd>{displayTime(agent.last_observed_at ?? latestEvent?.timestamp)}</dd>
          </div>
          <div>
            <dt>XP state</dt>
            <dd>{labelKey(claimStatus)}</dd>
          </div>
          <div>
            <dt>Review</dt>
            <dd>{xpStatus?.review_item_count ?? 0} claim flags</dd>
          </div>
          <div>
            <dt>Peer review</dt>
            <dd>{formatXp(currentCouncilXp)} current council XP / {currentCouncilVotes} votes</dd>
          </div>
        </dl>
        {showAllTimeCouncil && allTimeCouncil && (
          <details className="nested-stats council-history">
            <summary>All-time council record</summary>
            <div>
              <span>{formatXp(allTimeCouncil.peer_review_xp)} XP</span>
              <span>{allTimeCouncil.peer_review_assessment_count} votes</span>
              <span>{allTimeCouncil.peer_review_useful_count} useful</span>
              <span>{allTimeCouncil.peer_review_abstain_count} abstains</span>
            </div>
          </details>
        )}
        {candidateProfile && (
          <details className="nested-stats candidate-dossier">
            <summary>Candidate promotion dossier</summary>
            <div>
              <span>{labelKey(candidateProfile.promotion_level ?? candidateProfile.trust_level ?? "candidate")}</span>
              <span>{labelKey(candidateProfile.promotion_recommendation ?? "needs_more_evidence")}</span>
              {candidateProfile.promotion_review_cadence && <span>{candidateProfile.promotion_review_cadence}</span>}
            </div>
            {promotionDossier && (
              <dl className="candidate-dossier-list">
                <div>
                  <dt>Pros</dt>
                  <dd>{promotionDossier.pros.join(" ")}</dd>
                </div>
                <div>
                  <dt>Cons</dt>
                  <dd>{promotionDossier.cons.join(" ")}</dd>
                </div>
                <div>
                  <dt>Next gate</dt>
                  <dd>{promotionDossier.next_gate}</dd>
                </div>
              </dl>
            )}
          </details>
        )}
        <p>{agent.activity_reason ?? agent.summary ?? "No summary recorded."}</p>
        <div className="pill-row">
          <span className="pill">{stateLabel[agent.ui_state] ?? agent.ui_state}</span>
          <span className="pill">events: {xpStatus?.event_count ?? 0}</span>
          <span className="pill">current council: {currentCouncilVotes}</span>
          <span className={xpStatus?.review_item_count ? "pill attention" : "pill"}>{labelKey(claimStatus)}</span>
          {candidateProfile?.promotion_level && <span className="pill">{labelKey(candidateProfile.promotion_level)}</span>}
          {agent.visual_archetype && <span className="pill">{agent.visual_archetype}</span>}
          {agent.room && <span className="pill">{agent.room}</span>}
        </div>
      </div>
    </article>
  );
}
