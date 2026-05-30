import { useEffect, useState } from "react";
import {
  decideProposal,
  getAgents,
  getArtifacts,
  getCurrentSeason,
  getDashboardConfig,
  getEvents,
  getExpeditions,
  getHealth,
  getIncidents,
  getMemoryStores,
  getMilestones,
  getPlannedItems,
  getProposals,
  getRoutes,
  getRouteEdges,
  getRooms,
  getSeasonSummaries,
  completeProposalImplementation,
  requestProposalImplementation,
  reviewProposalImplementation,
  startProposalWork
} from "./api";
import type {
  Agent,
  Artifact,
  DashboardConfig,
  Event,
  Expedition,
  Health,
  Incident,
  MemoryStore,
  Milestone,
  PlannedItem,
  Proposal,
  ProposalDecision,
  Route,
  RouteEdge,
  RouteParticipant,
  Room,
  SeasonCurrent,
  SeasonSummary
} from "./types";
import { AgentCard } from "./components/AgentCard";
import { CurrentActivity } from "./components/CurrentActivity";
import { ExpeditionCard } from "./components/ExpeditionCard";
import { FieldReportCard } from "./components/FieldReportCard";
import { HQRooms } from "./components/HQRooms";
import { ReviewDesk } from "./components/ReviewDesk";
import { TrophyShelf } from "./components/TrophyShelf";
import { displayName, VisualToken } from "./components/VisualToken";

type TabId = "hq" | "expeditions" | "field-reports" | "proposal-desk" | "roster" | "systems";

const tabs: { id: TabId; label: string }[] = [
  { id: "hq", label: "HQ" },
  { id: "expeditions", label: "Expeditions" },
  { id: "field-reports", label: "Field Reports" },
  { id: "proposal-desk", label: "Planning Bureau" },
  { id: "roster", label: "Roster" },
  { id: "systems", label: "Systems" }
];

const visibleStates = ["awake", "on_call", "dormant", "blocked", "test_mode", "temporary_route"];

function countByState(agents: Agent[], incidents: Incident[]) {
  return visibleStates.map((state) => ({
    state,
    count: state === "blocked"
      ? agents.filter((agent) => agent.status.includes("blocked")).length + incidents.filter((incident) => incident.status === "open").length
      : agents.filter((agent) => agent.ui_state === state).length
  }));
}

function EmptyState({ label }: { label: string }) {
  return <p className="empty">{label}</p>;
}

function SectionHeader({ eyebrow, title, note }: { eyebrow: string; title: string; note?: string }) {
  return (
    <div className="section-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
      </div>
      {note && <span className="section-note">{note}</span>}
    </div>
  );
}

function formatXp(value = 0) {
  return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
}

function formatPercent(value = 0) {
  return `${Math.round(value * 100)}%`;
}

function formatMinutes(value = 0) {
  if (value < 60) return `${Math.round(value)}m`;
  const hours = Math.floor(value / 60);
  const minutes = Math.round(value % 60);
  return minutes ? `${hours}h ${minutes}m` : `${hours}h`;
}

function formatAgentCount(value: number) {
  return `${value} ${value === 1 ? "agent" : "agents"}`;
}

function formatShortDateTime(value?: string) {
  if (!value) return "not set";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  });
}

function labelize(value: string) {
  return value.replace(/_/g, " ");
}

function titleLabel(value: string) {
  const label = labelize(value);
  return label.charAt(0).toUpperCase() + label.slice(1);
}

function focusProposalCard(proposalId: string) {
  window.setTimeout(() => {
    const node = Array
      .from(document.querySelectorAll<HTMLElement>("[data-proposal-id]"))
      .find((element) => element.dataset.proposalId === proposalId);
    node?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, 80);
}

function proposalStatusLabel(status: Proposal["status"]) {
  if (status === "accepted") return "completed";
  if (status === "in_progress") return "queued for work";
  if (status === "implementation_requested") return "actual work";
  if (status === "implemented") return "final review";
  return labelize(status);
}

function agentClaimStatus(agent: Agent) {
  const counts = agent.xp_status?.claim_status_counts ?? {};
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  return entries[0]?.[0] ?? "no_claims";
}

function timestampInSeasonWindow(value: string | undefined, season: SeasonCurrent | null) {
  if (!value || !season?.started_at || !season.ends_at) return false;
  const timestamp = new Date(value).valueOf();
  const startedAt = new Date(season.started_at).valueOf();
  const endsAt = new Date(season.ends_at).valueOf();
  return Number.isFinite(timestamp)
    && Number.isFinite(startedAt)
    && Number.isFinite(endsAt)
    && timestamp >= startedAt
    && timestamp < endsAt;
}

function AgentXpBoard({ agents }: { agents: Agent[] }) {
  const ranked = [...agents]
    .sort((a, b) => (b.xp_status?.awarded_xp ?? 0) - (a.xp_status?.awarded_xp ?? 0))
    .slice(0, 6);

  return (
    <section className="living-section xp-board-section">
      <SectionHeader
        eyebrow="Agent XP Status"
        title="Calibration Scoreboard"
        note="Season 0.x visibility is a stress test, not final reputation."
      />
      <div className="xp-board">
        {ranked.map((agent) => {
          const xpStatus = agent.xp_status;
          const claimStatus = agentClaimStatus(agent);
          return (
            <article className="xp-agent-row" key={agent.id}>
              <VisualToken agent={agent} size="small" />
              <div>
                <h3>{displayName(agent)}</h3>
                <p>{agent.id}</p>
              </div>
              <strong>{formatXp(xpStatus?.awarded_xp ?? 0)} XP</strong>
              <div className="xp-agent-meta">
                <span>{xpStatus?.event_count ?? 0} events</span>
                <span>{xpStatus?.review_item_count ?? 0} review flags</span>
                <span>{formatXp(xpStatus?.peer_review_xp ?? 0)} current council XP</span>
                <span>{labelize(claimStatus)}</span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function SystemsView({
  routes,
  memoryStores,
  incidents,
  plannedItems,
  artifacts
}: {
  routes: Route[];
  memoryStores: MemoryStore[];
  incidents: Incident[];
  plannedItems: PlannedItem[];
  artifacts: Artifact[];
}) {
  return (
    <div className="tab-page">
      <SectionHeader eyebrow="Secondary Inventory" title="Systems, Routes, Archives" note="Visible here so the HQ page can stay readable." />
      <div className="split-grid">
        <section className="panel">
          <h3>Route Watch</h3>
          <div className="stack">
            {routes.map((route) => (
              <article className={`system-row route-${route.status}`} key={route.id}>
                <VisualToken label="RT" kind="system" size="small" state={route.status} />
                <div>
                  <h4>{route.id}</h4>
                  <p>{route.route}</p>
                  <span>{route.status}</span>
                  {route.risk && <p className="risk">{route.risk}</p>}
                </div>
              </article>
            ))}
          </div>
        </section>
        <section className="panel">
          <h3>Archive Vault</h3>
          <div className="stack">
            {memoryStores.map((store) => (
              <article className="system-row" key={store.id}>
                <VisualToken label="AR" kind="system" size="small" state="stable" />
                <div>
                  <h4>{store.id}</h4>
                  <p>{store.classification}</p>
                  {store.path && <span>{store.path}</span>}
                  {store.notes && <p className="risk">{store.notes}</p>}
                </div>
              </article>
            ))}
          </div>
        </section>
        <section className="panel">
          <h3>Incidents</h3>
          <div className="stack">
            {incidents.map((incident) => (
              <article className="system-row" key={incident.id}>
                <VisualToken label="IN" kind="system" size="small" state="blocked" />
                <div>
                  <h4>{incident.id}</h4>
                  <p>{incident.summary}</p>
                  {incident.impact && <p className="risk">{incident.impact}</p>}
                </div>
              </article>
            ))}
          </div>
        </section>
        <section className="panel">
          <h3>Blueprints And Artifacts</h3>
          <div className="stack">
            {plannedItems.map((item) => (
              <article className="system-row" key={item.id}>
                <VisualToken label="BP" kind="system" size="small" state={item.status} />
                <div>
                  <h4>{item.id}</h4>
                  <p>{item.classification}</p>
                  <span>{item.status}</span>
                </div>
              </article>
            ))}
            {artifacts.map((artifact) => (
              <article className="system-row" key={artifact.id}>
                <VisualToken label="AF" kind="system" size="small" state="stable" />
                <div>
                  <h4>{artifact.title}</h4>
                  <p>{artifact.summary}</p>
                  <span>{artifact.path}</span>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

const decisionButtonLabels: Record<ProposalDecision, string> = {
  approve: "Record Approval",
  deny: "Deny",
  revise: "Revise",
  defer: "Defer"
};

const decisionButtonTitles: Record<ProposalDecision, string> = {
  approve: "Approve Proposal - records approval only; does not implement.",
  deny: "Deny Proposal - records a local soft-wager denial only.",
  revise: "Request Revision - records a local clarification request only.",
  defer: "Defer Proposal - records a local deferral only."
};

const WORK_QUEUE_NEXT_STEP = "Actual work phase: use Implement Proposal to authorize a proposal-scoped OpenClaw route.";
const LEGACY_WORK_QUEUE_NOTES = new Set([
  "Moved into the local work queue. No implementation automation is launched.",
  "Queued for actual implementation. Next step: open a separate local work session from this proposal; no implementation automation is launched."
]);

const decisionActionNames: Record<ProposalDecision, string> = {
  approve: "Approve",
  deny: "Deny",
  revise: "Revise",
  defer: "Defer"
};

const decisionSubmitLabels: Record<ProposalDecision, string> = {
  approve: "Record Approval",
  deny: "Record Denial",
  revise: "Request Revision",
  defer: "Record Deferral"
};

const decisionTextareaLabels: Record<ProposalDecision, string> = {
  approve: "Optional: why is this worth pursuing?",
  deny: "Optional: what made this not worth pursuing?",
  revise: "Optional: what feels unclear, wrong, too broad, too narrow, or not quite right?",
  defer: "Optional: why should this wait?"
};

const decisionHelperText: Record<ProposalDecision, string> = {
  approve: "Useful notes explain the value, timing, and what should be true before implementation planning starts.",
  deny: "Useful notes identify the blocker, risk, low value, or mismatch so future proposals can avoid the same issue.",
  revise: "Useful notes help the agent ask better follow-up questions before resubmitting a narrower or clearer proposal.",
  defer: "Useful notes explain whether this should wait for timing, dependencies, risk reduction, or better evidence."
};

function ProposalAnalytics({
  proposals,
  currentSeason
}: {
  proposals: Proposal[];
  currentSeason: SeasonCurrent | null;
}) {
  const reputationProposals = proposals.filter((proposal) => !proposal.is_test_proposal && !proposal.excluded_from_reputation);
  const qaProposals = proposals.filter((proposal) => proposal.is_test_proposal || proposal.excluded_from_reputation);
  const councilVotes = proposals.flatMap((proposal) => proposal.council_votes ?? []);
  const currentCouncilVotes = currentSeason
    ? councilVotes.filter((vote) => timestampInSeasonWindow(vote.created_at, currentSeason))
    : councilVotes;
  const averageWager = reputationProposals.length
    ? reputationProposals.reduce((sum, proposal) => sum + proposal.requested_xp_wager, 0) / reputationProposals.length
    : 0;
  const averageConfidence = reputationProposals.length
    ? reputationProposals.reduce((sum, proposal) => sum + proposal.confidence, 0) / reputationProposals.length
    : 0;
  const simulatedAtRisk = reputationProposals
    .filter((proposal) => proposal.status === "pending")
    .reduce((sum, proposal) => sum + proposal.requested_xp_wager, 0);
  const simulatedLost = reputationProposals.reduce((sum, proposal) => sum + proposal.simulated_xp_loss, 0);
  const qaSimulatedLost = qaProposals.reduce((sum, proposal) => sum + proposal.simulated_xp_loss, 0);
  const decidedProposals = reputationProposals.filter((proposal) => Boolean(proposal.decision));
  const decisionsWithNotes = decidedProposals.filter((proposal) => proposal.decision_note_provided).length;
  const decisionsWithoutNotes = decidedProposals.length - decisionsWithNotes;
  const revisedProposals = reputationProposals.filter((proposal) => proposal.decision === "revise" || proposal.status === "revise_requested");
  const revisedWithUserContext = revisedProposals.filter((proposal) => proposal.decision_note_provided).length;
  const revisedWithoutUserContext = revisedProposals.length - revisedWithUserContext;
  const proposalsEnteringDialogue = reputationProposals.filter((proposal) =>
    proposal.status === "revise_requested"
    || (proposal.dialogue_messages ?? []).some((message) => message.message_type === "clarification_question")
  ).length;
  const countsByType = countProposals(reputationProposals, (proposal) => proposal.proposal_type);
  const countsByDecision = countProposals(reputationProposals, (proposal) => proposal.decision ?? proposal.status);
  const countsByAgent = countProposals(reputationProposals, (proposal) => proposal.source_agent);
  const countsByVote = councilVotes.reduce<Record<string, number>>((counts, vote) => {
    counts[vote.vote] = (counts[vote.vote] ?? 0) + 1;
    return counts;
  }, {});
  const currentCountsByVote = currentCouncilVotes.reduce<Record<string, number>>((counts, vote) => {
    counts[vote.vote] = (counts[vote.vote] ?? 0) + 1;
    return counts;
  }, {});
  const allTimePeerReviewXp = proposals.reduce((sum, proposal) => sum + (proposal.council_summary?.peer_review_xp_awarded ?? 0), 0);
  const currentPeerReviewXp = currentCouncilVotes.reduce((sum, vote) => sum + vote.peer_review_xp, 0);
  const allTimeUsefulAssessments = councilVotes.filter((vote) => vote.usefulness_status === "useful").length;
  const currentUsefulAssessments = currentCouncilVotes.filter((vote) => vote.usefulness_status === "useful").length;

  return (
    <section className="living-section proposal-analytics">
      <SectionHeader
        eyebrow="Council Ledger"
        title="Suggestion Calibration"
        note={`Current season ${currentSeason?.season ?? "unknown"} first; all-time history is nested below.`}
      />
      <div className="proposal-metrics">
        <div><strong>{reputationProposals.length}</strong><span>normal proposals</span></div>
        <div><strong>{qaProposals.length}</strong><span>QA test proposals</span></div>
        <div><strong>{currentCouncilVotes.length}</strong><span>current council votes</span></div>
        <div><strong>{currentCountsByVote.abstain ?? 0}</strong><span>current abstains</span></div>
        <div><strong>{currentUsefulAssessments}</strong><span>current useful reviews</span></div>
        <div><strong>{formatXp(currentPeerReviewXp)}</strong><span>current council XP</span></div>
        <div><strong>{formatXp(averageWager)}</strong><span>normal avg wager</span></div>
        <div><strong>{formatPercent(averageConfidence)}</strong><span>normal avg confidence</span></div>
        <div><strong>{formatXp(simulatedAtRisk)}</strong><span>normal XP at risk</span></div>
        <div><strong>{formatXp(simulatedLost)}</strong><span>normal XP lost</span></div>
        <div><strong>{formatXp(qaSimulatedLost)}</strong><span>QA simulated XP lost</span></div>
        <div><strong>{decisionsWithNotes}</strong><span>decisions with notes</span></div>
        <div><strong>{decisionsWithoutNotes}</strong><span>decisions without notes</span></div>
        <div><strong>{revisedWithUserContext}</strong><span>revised with context</span></div>
        <div><strong>{revisedWithoutUserContext}</strong><span>revised without context</span></div>
        <div><strong>{proposalsEnteringDialogue}</strong><span>entered dialogue</span></div>
      </div>
      <details className="nested-stats proposal-history">
        <summary>All-time council history</summary>
        <div className="proposal-metrics nested-metrics">
          <div><strong>{councilVotes.length}</strong><span>all-time specialist votes</span></div>
          <div><strong>{countsByVote.abstain ?? 0}</strong><span>all-time abstains</span></div>
          <div><strong>{allTimeUsefulAssessments}</strong><span>all-time useful reviews</span></div>
          <div><strong>{formatXp(allTimePeerReviewXp)}</strong><span>all-time council XP</span></div>
        </div>
      </details>
      <div className="proposal-breakdown-grid">
        <Breakdown title="Count By Type" counts={countsByType} />
        <Breakdown title="Decision And Status Counts" counts={countsByDecision} />
        <Breakdown title="Proposals By Agent" counts={countsByAgent} />
        <Breakdown title="Council Votes" counts={countsByVote} />
      </div>
    </section>
  );
}

function countProposals(proposals: Proposal[], selector: (proposal: Proposal) => string) {
  return proposals.reduce<Record<string, number>>((counts, proposal) => {
    const key = selector(proposal);
    counts[key] = (counts[key] ?? 0) + 1;
    return counts;
  }, {});
}

function Breakdown({ title, counts }: { title: string; counts: Record<string, number> }) {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  return (
    <div className="panel proposal-breakdown">
      <h3>{title}</h3>
      {entries.length ? (
        <div className="stack">
          {entries.map(([key, count]) => (
            <div className="proposal-count-row" key={key}>
              <span>{labelize(key)}</span>
              <strong>{count}</strong>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState label="No proposal records are available." />
      )}
    </div>
  );
}

function ProposalSection({
  title,
  note,
  proposals,
  onDecision,
  onStartWork,
  onRequestImplementation,
  onCompleteImplementation,
  onReviewImplementation,
  decisionPending,
  workPending,
  implementationPending,
  agentById,
  recentlyFocusedProposalId
}: {
  title: string;
  note: string;
  proposals: Proposal[];
  onDecision: (proposal: Proposal, decision: ProposalDecision) => void;
  onStartWork: (proposal: Proposal) => void;
  onRequestImplementation: (proposal: Proposal) => void;
  onCompleteImplementation: (proposal: Proposal) => void;
  onReviewImplementation: (proposal: Proposal, decision: "accept" | "reject") => void;
  decisionPending: string | null;
  workPending: string | null;
  implementationPending: string | null;
  agentById: Map<string, Agent>;
  recentlyFocusedProposalId: string | null;
}) {
  return (
    <section className="living-section">
      <SectionHeader eyebrow="Planning Bureau" title={title} note={note} />
      <div className="proposal-grid">
        {proposals.length
          ? proposals.map((proposal) => (
            <ProposalCard
              key={proposal.proposal_id}
              proposal={proposal}
              onDecision={onDecision}
              onStartWork={onStartWork}
              onRequestImplementation={onRequestImplementation}
              onCompleteImplementation={onCompleteImplementation}
              onReviewImplementation={onReviewImplementation}
              decisionPending={decisionPending === proposal.proposal_id}
              workPending={workPending === proposal.proposal_id}
              implementationPending={implementationPending === proposal.proposal_id}
              agentById={agentById}
              isRecentlyFocused={recentlyFocusedProposalId === proposal.proposal_id}
            />
          ))
          : <EmptyState label="No proposals in this section." />}
      </div>
    </section>
  );
}

function RouteParticipantList({ title, items }: { title: string; items: RouteParticipant[] }) {
  return (
    <div className="route-policy-block">
      <strong>{title}</strong>
      {items.length ? (
        <ul className="route-participant-list">
          {items.map((item) => {
            const label = item.agent_id || item.provider || "unknown-provider";
            const meta = [
              item.provider,
              item.task_role ? labelize(item.task_role) : undefined,
              item.trust_level ? labelize(item.trust_level) : undefined,
              item.route_status ? labelize(item.route_status) : undefined
            ].filter(Boolean).join(" / ");
            return (
              <li key={`${title}-${label}`}>
                <strong>{label}</strong>
                {meta && <p>{meta}</p>}
                {item.cost_quota_notes && <small>{item.cost_quota_notes}</small>}
                {item.unavailable_reason && <em>Skipped: {item.unavailable_reason}</em>}
              </li>
            );
          })}
        </ul>
      ) : (
        <p>None recorded.</p>
      )}
    </div>
  );
}

function ProposalCard({
  proposal,
  onDecision,
  onStartWork,
  onRequestImplementation,
  onCompleteImplementation,
  onReviewImplementation,
  decisionPending,
  workPending,
  implementationPending,
  agentById,
  isRecentlyFocused
}: {
  proposal: Proposal;
  onDecision: (proposal: Proposal, decision: ProposalDecision) => void;
  onStartWork: (proposal: Proposal) => void;
  onRequestImplementation: (proposal: Proposal) => void;
  onCompleteImplementation: (proposal: Proposal) => void;
  onReviewImplementation: (proposal: Proposal, decision: "accept" | "reject") => void;
  decisionPending: boolean;
  workPending: boolean;
  implementationPending: boolean;
  agentById: Map<string, Agent>;
  isRecentlyFocused: boolean;
}) {
  const hasDecisionNote = Boolean(proposal.decision_note);
  const canDecide = proposal.status === "pending";
  const canStartWork = proposal.status === "approved";
  const canRequestImplementation = proposal.status === "in_progress";
  const canCompleteImplementation = proposal.status === "implementation_requested";
  const canReviewImplementation = proposal.status === "implemented";
  const routePlan = proposal.implementation_route_plan;
  const selectedRouteAgents = routePlan?.selected_agents ?? [];
  const candidateProviders = routePlan?.candidate_providers ?? [];
  const skippedProviders = routePlan?.skipped_providers ?? [];
  const providerRoles = routePlan?.provider_roles ?? [];
  const tokenSavingChoices = routePlan?.token_saving_choices ?? [];
  const showWorkStartNote = Boolean(
    proposal.work_start_note
      && proposal.work_start_note !== WORK_QUEUE_NEXT_STEP
      && !LEGACY_WORK_QUEUE_NOTES.has(proposal.work_start_note)
  );
  const eligibleCount = proposal.council_summary?.eligible_count ?? proposal.eligible_agent_ids?.length ?? 0;
  const amendmentRequestedCount = proposal.council_summary?.amendment_requested_count
    ?? (proposal.council_votes ?? []).filter((vote) => vote.response_kind === "required_abstain").length;
  const peerReviewParticipationCount = proposal.council_summary?.peer_review_participation_count
    ?? Math.max((proposal.council_summary?.participation_count ?? proposal.council_votes?.length ?? 0) - amendmentRequestedCount, 0);
  const clarificationQuestions = (proposal.dialogue_messages ?? []).filter(
    (message) => message.message_type === "clarification_question"
  );
  return (
    <article
      className={`proposal-card risk-${proposal.risk_level}${isRecentlyFocused ? " recently-focused" : ""}`}
      data-proposal-id={proposal.proposal_id}
    >
      <div className="proposal-card-header">
        <div>
          <p className="eyebrow">{labelize(proposal.proposal_type)}</p>
          <h3>{proposal.title}</h3>
          <p>{proposal.summary}</p>
        </div>
        <span className="badge">{proposalStatusLabel(proposal.status)}</span>
      </div>

      {proposal.is_test_proposal && (
        <div className="proposal-test-note">
          <strong>QA test-only denial probe</strong>
          <span>
            Expected decision: {proposal.expected_decision ?? "deny"}. Excluded from normal proposal reputation analytics.
          </span>
        </div>
      )}

      <div className="proposal-facts">
        <div><span>source agent</span><strong>{proposal.source_agent}</strong></div>
        <div><span>broadcast</span><strong>{labelize(proposal.broadcast_status ?? "broadcasted")}</strong></div>
        <div>
          <span>eligible specialists</span>
          <strong>{eligibleCount}</strong>
        </div>
        <div>
          <span>peer reviews</span>
          <strong>{peerReviewParticipationCount}/{eligibleCount}</strong>
        </div>
        <div>
          <span>amend requests</span>
          <strong>{amendmentRequestedCount}</strong>
        </div>
        <div><span>confidence</span><strong>{formatPercent(proposal.confidence)}</strong></div>
        <div><span>requested wager</span><strong>{formatXp(proposal.requested_xp_wager)} XP</strong></div>
        <div><span>estimated active time</span><strong>{formatMinutes(proposal.estimated_active_minutes)}</strong></div>
        <div><span>risk level</span><strong>{proposal.risk_level}</strong></div>
      </div>

      <p className="proposal-reasoning">{proposal.reasoning}</p>

      <CouncilReview proposal={proposal} agentById={agentById} />

      <div className="proposal-detail-grid">
        <ListBlock title="Affected Areas" items={proposal.affected_areas} />
        <ListBlock title="Acceptance Criteria" items={proposal.acceptance_criteria} />
      </div>

      <div className="proposal-rollback">
        <span>Rollback plan</span>
        <p>{proposal.rollback_plan}</p>
      </div>

      {hasDecisionNote && (
        <div className="proposal-decision-note">
          <span>Decision note</span>
          <p>{proposal.decision_note}</p>
        </div>
      )}

      {proposal.work_started_at && (
        <div className="proposal-work-note">
          <span>Queued for work</span>
          <p>{formatShortDateTime(proposal.work_started_at)}</p>
          {showWorkStartNote && <p>{proposal.work_start_note}</p>}
          <p>{WORK_QUEUE_NEXT_STEP}</p>
          {canRequestImplementation && (
            <div className="proposal-inline-actions">
              <button
                disabled={implementationPending}
                onClick={() => onRequestImplementation(proposal)}
                title="Authorize proposal-scoped OpenClaw routing and record the provider-agnostic route snapshot."
                type="button"
              >
                {implementationPending ? "Requesting Implementation" : "Implement Proposal"}
              </button>
            </div>
          )}
        </div>
      )}

      {proposal.implementation_requested_at && (
        <div className="proposal-work-note">
          <span>Actual work</span>
          <p>{formatShortDateTime(proposal.implementation_requested_at)}</p>
          {proposal.implementation_request_note && <p>{proposal.implementation_request_note}</p>}
          {proposal.implementation_brief_path && <p>Brief: {proposal.implementation_brief_path}</p>}
          {proposal.implementation_dispatch_status && <p>Dispatch: {labelize(proposal.implementation_dispatch_status)}</p>}
          {routePlan?.dispatch_job_path && <p>Dispatch job: {routePlan.dispatch_job_path}</p>}
          <details className="nested-stats">
            <summary>OpenClaw route snapshot</summary>
            <div className="nested-metrics">
              <div><span>owner</span><strong>{routePlan?.routing_owner ?? routePlan?.orchestration_layer ?? "OpenClaw"}</strong></div>
              <div><span>primary router</span><strong>{routePlan?.primary_provider ?? "openclaw_router"}</strong></div>
              <div><span>mode</span><strong>{labelize(routePlan?.dispatch_mode ?? "openclaw_provider_agnostic")}</strong></div>
              <div><span>final reviewer</span><strong>{routePlan?.final_reviewer_id ?? "august"}</strong></div>
            </div>
            {providerRoles.length > 0 && <p>Roles: {providerRoles.map(labelize).join(", ")}</p>}
            <RouteParticipantList title="Selected agents" items={selectedRouteAgents} />
            <RouteParticipantList title="Cross-reference candidates" items={candidateProviders} />
            <RouteParticipantList title="Unavailable or skipped" items={skippedProviders} />
            {tokenSavingChoices.length > 0 && (
              <div className="route-policy-block">
                <strong>Token-saving choices</strong>
                <ul>
                  {tokenSavingChoices.map((choice) => <li key={choice}>{choice}</li>)}
                </ul>
              </div>
            )}
            {routePlan?.promotion_policy && <p>{routePlan.promotion_policy}</p>}
          </details>
          {canCompleteImplementation && (
            <div className="proposal-inline-actions">
              <button
                disabled={implementationPending}
                onClick={() => onCompleteImplementation(proposal)}
                title="Mark implementation complete and move it to final review. Evidence can be added through the API or later workflow."
                type="button"
              >
                {implementationPending ? "Marking Implemented" : "Mark Implemented"}
              </button>
            </div>
          )}
        </div>
      )}

      {proposal.implementation_completed_at && (
        <div className="proposal-work-note">
          <span>Final review</span>
          <p>{formatShortDateTime(proposal.implementation_completed_at)}</p>
          {proposal.implementation_completion_note && <p>{proposal.implementation_completion_note}</p>}
          {proposal.implementation_evidence_refs?.length ? (
            <ul>
              {proposal.implementation_evidence_refs.map((ref) => <li key={ref}>{ref}</li>)}
            </ul>
          ) : <p>No evidence refs recorded yet.</p>}
          {canReviewImplementation && (
            <div className="proposal-inline-actions">
              <button
                disabled={implementationPending}
                onClick={() => onReviewImplementation(proposal, "accept")}
                title="Accept this implementation and move the proposal to Completed."
                type="button"
              >
                Accept Implementation
              </button>
              <button
                disabled={implementationPending}
                onClick={() => onReviewImplementation(proposal, "reject")}
                title="Reject this implementation after final review."
                type="button"
              >
                Reject
              </button>
            </div>
          )}
          {proposal.implementation_reviewed_at && (
            <p>Reviewed by {proposal.implementation_reviewer_id ?? "august"} on {formatShortDateTime(proposal.implementation_reviewed_at)}.</p>
          )}
        </div>
      )}

      {proposal.status === "revise_requested" && (
        <div className="proposal-clarification">
          <span>Clarification needed</span>
          <p>Revision starts a dialogue. The agent should ask follow-up questions before resubmitting.</p>
          <ul>
            {clarificationQuestions.length
              ? clarificationQuestions.map((message) => <li key={message.message_id}>{message.message}</li>)
              : <li>What would make this proposal acceptable?</li>}
          </ul>
        </div>
      )}

      <div className="proposal-wager-row">
        <span>simulated gain {formatXp(proposal.simulated_xp_gain)} XP</span>
        <span>simulated loss {formatXp(proposal.simulated_xp_loss)} XP</span>
      </div>

      {canDecide && (
        <div className="proposal-actions">
          {(["approve", "deny", "revise", "defer"] as ProposalDecision[]).map((decision) => (
            <button
              aria-label={decisionButtonTitles[decision]}
              disabled={decisionPending}
              key={decision}
              onClick={() => onDecision(proposal, decision)}
              title={decisionButtonTitles[decision]}
              type="button"
            >
              {decisionButtonLabels[decision]}
            </button>
          ))}
        </div>
      )}

      {canStartWork && (
        <div className="proposal-actions work-actions">
          <button
            aria-label="Start local work on approved proposal"
            disabled={workPending}
            onClick={() => onStartWork(proposal)}
            title="Move this approved proposal into the local work queue. Actual implementation still requires a separate local work session."
            type="button"
          >
            {workPending ? "Queueing Work" : "Queue Work"}
          </button>
        </div>
      )}
    </article>
  );
}

function CouncilReview({ proposal, agentById }: { proposal: Proposal; agentById: Map<string, Agent> }) {
  const votes = proposal.council_votes ?? [];
  const summary = proposal.council_summary;
  const counts = summary?.vote_counts ?? { support: 0, oppose: 0, abstain: 0 };
  const eligibleCount = summary?.eligible_count ?? proposal.eligible_agent_ids.length;
  const amendmentRequestedCount = summary?.amendment_requested_count
    ?? votes.filter((vote) => vote.response_kind === "required_abstain").length;
  const peerReviewParticipationCount = summary?.peer_review_participation_count
    ?? Math.max((summary?.participation_count ?? votes.length) - amendmentRequestedCount, 0);
  const voteGroups = (["support", "oppose", "abstain"] as const).map((voteValue) => ({
    voteValue,
    votes: votes.filter((vote) => vote.vote === voteValue)
  }));
  return (
    <div className="council-review">
      <div className="council-response-meta">
        <div>
          <span>peer reviews</span>
          <strong>{peerReviewParticipationCount}/{eligibleCount}</strong>
        </div>
        <div>
          <span>amendments needed</span>
          <strong>{amendmentRequestedCount}</strong>
        </div>
        <div>
          <span>useful peer XP</span>
          <strong>{formatXp(summary?.peer_review_xp_awarded ?? 0)}</strong>
        </div>
      </div>
      <p className="council-guidance">
        {summary?.guidance ?? "Abstain is healthy when a specialist does not know enough to make a useful call."}
      </p>
      <div className="council-drawer-list">
        {voteGroups.map(({ voteValue, votes: groupVotes }) => (
          <CouncilVoteDrawer
            agentById={agentById}
            count={counts[voteValue] ?? groupVotes.length}
            key={voteValue}
            voteValue={voteValue}
            votes={groupVotes}
          />
        ))}
      </div>
    </div>
  );
}

function CouncilVoteDrawer({
  voteValue,
  votes,
  count,
  agentById
}: {
  voteValue: "support" | "oppose" | "abstain";
  votes: Proposal["council_votes"];
  count: number;
  agentById: Map<string, Agent>;
}) {
  return (
    <details className={`council-vote-drawer vote-${voteValue}`}>
      <summary>
        <strong>{titleLabel(voteValue)}: {formatAgentCount(count)}</strong>
      </summary>
      {votes.length ? (
        <div className="council-vote-list">
          {votes.map((vote) => {
            const agent = agentById.get(vote.agent_id);
            const needsAmendment = vote.response_kind === "required_abstain";
            const wasNudged = vote.response_kind === "amended_after_prompt";
            return (
              <article className={`council-vote vote-${vote.vote}`} key={vote.vote_id}>
                <div className="council-vote-header">
                  <div>
                    <span>{needsAmendment ? "amendment requested" : wasNudged ? "late amendment" : vote.vote}</span>
                    <h4>{agent ? displayName(agent) : vote.agent_id}</h4>
                  </div>
                  <strong>{formatPercent(vote.confidence)}</strong>
                </div>
                <p>{vote.reasoning}</p>
                <dl className="vote-notes">
                  <div>
                    <dt>Benefit</dt>
                    <dd>{vote.expected_benefit}</dd>
                  </div>
                  <div>
                    <dt>If it fails</dt>
                    <dd>{vote.expected_failure_mode}</dd>
                  </div>
                  <div>
                    <dt>Risk</dt>
                    <dd>{vote.risk_notes}</dd>
                  </div>
                  {vote.context_notes && (
                    <div>
                      <dt>Context</dt>
                      <dd>{vote.context_notes}</dd>
                    </div>
                  )}
                </dl>
                {vote.peer_review_xp > 0 && (
                  <span className="peer-xp-chip">useful assessment +{formatXp(vote.peer_review_xp)} peer XP</span>
                )}
                {needsAmendment && (
                  <span className="amendment-chip">amend support, oppose, or useful abstain reasoning for peer-review XP</span>
                )}
                {wasNudged && (
                  <span className="late-penalty-chip">
                    late participation: {formatPercent(vote.peer_review_xp_multiplier ?? 0.5)} peer XP cap
                  </span>
                )}
              </article>
            );
          })}
        </div>
      ) : (
        <p className="empty">No {voteValue} responses.</p>
      )}
    </details>
  );
}

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="proposal-list-block">
      <span>{title}</span>
      {items.length ? (
        <ul>
          {items.map((item) => <li key={item}>{item}</li>)}
        </ul>
      ) : (
        <p>None listed.</p>
      )}
    </div>
  );
}

function DecisionDialog({
  proposal,
  decision,
  note,
  onNoteChange,
  onCancel,
  onSubmit,
  isSubmitting
}: {
  proposal: Proposal;
  decision: ProposalDecision;
  note: string;
  onNoteChange: (value: string) => void;
  onCancel: () => void;
  onSubmit: () => void;
  isSubmitting: boolean;
}) {
  const textareaId = `decision-note-${proposal.proposal_id}-${decision}`;
  return (
    <div className="dialog-backdrop" role="presentation">
      <section className="decision-dialog" role="dialog" aria-modal="true" aria-labelledby="decision-dialog-title">
        <div className="decision-dialog-header">
          <div>
            <p className="eyebrow">Planning Bureau Decision</p>
            <h2 id="decision-dialog-title">{proposal.title}</h2>
          </div>
          <span className="badge">{decisionActionNames[decision]}</span>
        </div>

        <div className="proposal-facts decision-dialog-facts">
          <div><span>requested wager</span><strong>{formatXp(proposal.requested_xp_wager)} XP</strong></div>
          <div><span>confidence</span><strong>{formatPercent(proposal.confidence)}</strong></div>
          <div><span>risk level</span><strong>{proposal.risk_level}</strong></div>
        </div>

        <p className="decision-local-only">
          This records a local Planning Bureau decision only. It does not implement the suggestion.
        </p>

        <label className="decision-note-field" htmlFor={textareaId}>
          <span>{decisionTextareaLabels[decision]}</span>
          <textarea
            id={textareaId}
            onChange={(event) => onNoteChange(event.target.value)}
            placeholder="Notes are optional during Season 0.x."
            rows={5}
            value={note}
          />
        </label>
        <p className="decision-helper">{decisionHelperText[decision]}</p>

        <div className="dialog-actions">
          <button onClick={onCancel} type="button">Cancel</button>
          <button disabled={isSubmitting} onClick={onSubmit} type="button">
            {decisionSubmitLabels[decision]}
          </button>
        </div>
      </section>
    </div>
  );
}

function ProposalDeskView({
  proposals,
  onDecision,
  onStartWork,
  onRequestImplementation,
  onCompleteImplementation,
  onReviewImplementation,
  decisionPending,
  workPending,
  implementationPending,
  agentById,
  currentSeason,
  recentlyFocusedProposalId
}: {
  proposals: Proposal[];
  onDecision: (proposal: Proposal, decision: ProposalDecision) => void;
  onStartWork: (proposal: Proposal) => void;
  onRequestImplementation: (proposal: Proposal) => void;
  onCompleteImplementation: (proposal: Proposal) => void;
  onReviewImplementation: (proposal: Proposal, decision: "accept" | "reject") => void;
  decisionPending: string | null;
  workPending: string | null;
  implementationPending: string | null;
  agentById: Map<string, Agent>;
  currentSeason: SeasonCurrent | null;
  recentlyFocusedProposalId: string | null;
}) {
  const pending = proposals.filter((proposal) => ["draft", "pending", "revise_requested"].includes(proposal.status));
  const approved = proposals.filter((proposal) => proposal.status === "approved");
  const working = proposals.filter((proposal) => proposal.status === "in_progress");
  const implementationRequested = proposals.filter((proposal) => proposal.status === "implementation_requested");
  const implementedReview = proposals.filter((proposal) => proposal.status === "implemented");
  const completed = proposals.filter((proposal) => proposal.status === "accepted");
  const denied = proposals.filter((proposal) => ["denied", "rejected"].includes(proposal.status));
  const deferred = proposals.filter((proposal) => ["deferred", "archived"].includes(proposal.status));

  return (
    <div className="tab-page proposal-desk-page">
      <section className="today-panel proposal-desk-intro">
        <div>
          <p className="eyebrow">Local-only Planning</p>
          <h2>Council of Specialists</h2>
          <p>
            Proposals are broadcast to eligible specialists for support, oppose, or abstain advice. Their simple
            reasoning is shown here before August records any local decision.
          </p>
        </div>
        <div className="state-summary" aria-label="Planning Bureau safety posture">
          <div className="state-chip state-awake"><span className="state-dot" /><strong>local</strong><span>SQLite only</span></div>
          <div className="state-chip state-test_mode"><span className="state-dot" /><strong>vote</strong><span>confidence notes</span></div>
          <div className="state-chip state-on_call"><span className="state-dot" /><strong>abstain</strong><span>is healthy</span></div>
          <div className="state-chip state-dormant"><span className="state-dot" /><strong>no</strong><span>auto implementation</span></div>
        </div>
      </section>

      <ProposalSection
        title="Pending Proposals"
        note={`${pending.length} awaiting decision or clarification`}
        proposals={pending}
        onDecision={onDecision}
        onStartWork={onStartWork}
        onRequestImplementation={onRequestImplementation}
        onCompleteImplementation={onCompleteImplementation}
        onReviewImplementation={onReviewImplementation}
        decisionPending={decisionPending}
        workPending={workPending}
        implementationPending={implementationPending}
        agentById={agentById}
        recentlyFocusedProposalId={recentlyFocusedProposalId}
      />
      <ProposalSection
        title="Approved, Not Started"
        note={`${approved.length} approved with no local work-start event yet`}
        proposals={approved}
        onDecision={onDecision}
        onStartWork={onStartWork}
        onRequestImplementation={onRequestImplementation}
        onCompleteImplementation={onCompleteImplementation}
        onReviewImplementation={onReviewImplementation}
        decisionPending={decisionPending}
        workPending={workPending}
        implementationPending={implementationPending}
        agentById={agentById}
        recentlyFocusedProposalId={recentlyFocusedProposalId}
      />
      <ProposalSection
        title="Work Queue"
        note={`${working.length} queued for implementation authorization through Implement Proposal`}
        proposals={working}
        onDecision={onDecision}
        onStartWork={onStartWork}
        onRequestImplementation={onRequestImplementation}
        onCompleteImplementation={onCompleteImplementation}
        onReviewImplementation={onReviewImplementation}
        decisionPending={decisionPending}
        workPending={workPending}
        implementationPending={implementationPending}
        agentById={agentById}
        recentlyFocusedProposalId={recentlyFocusedProposalId}
      />
      <ProposalSection
        title="Actual Work"
        note={`${implementationRequested.length} implementation request${implementationRequested.length === 1 ? "" : "s"} with local briefs and OpenClaw route snapshots`}
        proposals={implementationRequested}
        onDecision={onDecision}
        onStartWork={onStartWork}
        onRequestImplementation={onRequestImplementation}
        onCompleteImplementation={onCompleteImplementation}
        onReviewImplementation={onReviewImplementation}
        decisionPending={decisionPending}
        workPending={workPending}
        implementationPending={implementationPending}
        agentById={agentById}
        recentlyFocusedProposalId={recentlyFocusedProposalId}
      />
      <ProposalSection
        title="Final Review"
        note={`${implementedReview.length} implemented proposal${implementedReview.length === 1 ? "" : "s"} waiting for August acceptance`}
        proposals={implementedReview}
        onDecision={onDecision}
        onStartWork={onStartWork}
        onRequestImplementation={onRequestImplementation}
        onCompleteImplementation={onCompleteImplementation}
        onReviewImplementation={onReviewImplementation}
        decisionPending={decisionPending}
        workPending={workPending}
        implementationPending={implementationPending}
        agentById={agentById}
        recentlyFocusedProposalId={recentlyFocusedProposalId}
      />
      <ProposalSection
        title="Completed"
        note={`${completed.length} accepted proposal outcome${completed.length === 1 ? "" : "s"} after final review`}
        proposals={completed}
        onDecision={onDecision}
        onStartWork={onStartWork}
        onRequestImplementation={onRequestImplementation}
        onCompleteImplementation={onCompleteImplementation}
        onReviewImplementation={onReviewImplementation}
        decisionPending={decisionPending}
        workPending={workPending}
        implementationPending={implementationPending}
        agentById={agentById}
        recentlyFocusedProposalId={recentlyFocusedProposalId}
      />
      <ProposalSection
        title="Denied Proposals"
        note={`${denied.length} recorded with simulated wager outcomes`}
        proposals={denied}
        onDecision={onDecision}
        onStartWork={onStartWork}
        onRequestImplementation={onRequestImplementation}
        onCompleteImplementation={onCompleteImplementation}
        onReviewImplementation={onReviewImplementation}
        decisionPending={decisionPending}
        workPending={workPending}
        implementationPending={implementationPending}
        agentById={agentById}
        recentlyFocusedProposalId={recentlyFocusedProposalId}
      />
      <ProposalSection
        title="Deferred Proposals"
        note={`${deferred.length} archived for later review`}
        proposals={deferred}
        onDecision={onDecision}
        onStartWork={onStartWork}
        onRequestImplementation={onRequestImplementation}
        onCompleteImplementation={onCompleteImplementation}
        onReviewImplementation={onReviewImplementation}
        decisionPending={decisionPending}
        workPending={workPending}
        implementationPending={implementationPending}
        agentById={agentById}
        recentlyFocusedProposalId={recentlyFocusedProposalId}
      />
      <ProposalAnalytics proposals={proposals} currentSeason={currentSeason} />
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>("hq");
  const [health, setHealth] = useState<Health | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [expeditions, setExpeditions] = useState<Expedition[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [routeEdges, setRouteEdges] = useState<RouteEdge[]>([]);
  const [memoryStores, setMemoryStores] = useState<MemoryStore[]>([]);
  const [plannedItems, setPlannedItems] = useState<PlannedItem[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [currentSeasonState, setCurrentSeasonState] = useState<SeasonCurrent | null>(null);
  const [seasonSummaries, setSeasonSummaries] = useState<SeasonSummary[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [dashboardConfig, setDashboardConfig] = useState<DashboardConfig | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [decisionPending, setDecisionPending] = useState<string | null>(null);
  const [workPending, setWorkPending] = useState<string | null>(null);
  const [implementationPending, setImplementationPending] = useState<string | null>(null);
  const [recentlyFocusedProposalId, setRecentlyFocusedProposalId] = useState<string | null>(null);
  const [pendingDecision, setPendingDecision] = useState<{ proposal: Proposal; decision: ProposalDecision } | null>(null);
  const [decisionNoteDraft, setDecisionNoteDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const loadData = () => {
      Promise.all([
        getHealth(),
        getAgents(),
        getExpeditions(),
        getEvents(),
        getMilestones(),
        getIncidents(),
        getRoutes(),
        getRooms(),
        getRouteEdges(),
        getMemoryStores(),
        getPlannedItems(),
        getArtifacts(),
        getCurrentSeason().catch((err) => {
          console.warn("Current season endpoint unavailable; using health and summary fallback.", err);
          return null;
        }),
        getSeasonSummaries(),
        getProposals(),
        getDashboardConfig()
      ])
      .then(([apiHealth, a, ex, ev, ms, inc, rt, roomRows, edgeRows, mem, planned, art, activeSeason, summaries, prop, config]) => {
        if (cancelled) return;
        setHealth(apiHealth);
        setAgents(a);
        setExpeditions(ex);
        setEvents(ev);
        setMilestones(ms);
        setIncidents(inc);
        setRoutes(rt);
        setRooms(roomRows);
        setRouteEdges(edgeRows);
        setMemoryStores(mem);
        setPlannedItems(planned);
        setArtifacts(art);
        setCurrentSeasonState(activeSeason);
        setSeasonSummaries(summaries);
        setProposals(prop);
        setDashboardConfig(config);
        setLastUpdated(new Date().toLocaleTimeString());
        setError(null);
      })
      .catch((err) => {
        if (cancelled) return;
        setHealth(null);
        setError(String(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    };

    loadData();
    const refreshSeconds = dashboardConfig?.refresh_seconds ?? 15;
    const interval = window.setInterval(loadData, Math.max(5, refreshSeconds) * 1000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [dashboardConfig?.refresh_seconds]);

  const openDecisionDialog = (proposal: Proposal, decision: ProposalDecision) => {
    setPendingDecision({ proposal, decision });
    setDecisionNoteDraft("");
  };

  const closeDecisionDialog = () => {
    if (decisionPending) return;
    setPendingDecision(null);
    setDecisionNoteDraft("");
  };

  const markProposalChanged = (proposalId: string) => {
    setRecentlyFocusedProposalId(proposalId);
    focusProposalCard(proposalId);
    window.setTimeout(() => {
      setRecentlyFocusedProposalId((current) => current === proposalId ? null : current);
    }, 2800);
  };

  const submitProposalDecision = async () => {
    if (!pendingDecision) return;
    const { proposal, decision } = pendingDecision;
    setDecisionPending(proposal.proposal_id);
    try {
      const updated = await decideProposal(proposal.proposal_id, decision, decisionNoteDraft.trim());
      setProposals((current) => current.map((item) => item.proposal_id === updated.proposal_id ? updated : item));
      setEvents(await getEvents());
      markProposalChanged(updated.proposal_id);
      setPendingDecision(null);
      setDecisionNoteDraft("");
      setError(null);
    } catch (err) {
      setError(String(err));
    } finally {
      setDecisionPending(null);
    }
  };

  const handleStartProposalWork = async (proposal: Proposal) => {
    setWorkPending(proposal.proposal_id);
    try {
      const updated = await startProposalWork(proposal.proposal_id);
      setProposals((current) => current.map((item) => item.proposal_id === updated.proposal_id ? updated : item));
      setEvents(await getEvents());
      markProposalChanged(updated.proposal_id);
      setError(null);
    } catch (err) {
      setError(String(err));
    } finally {
      setWorkPending(null);
    }
  };

  const handleRequestImplementation = async (proposal: Proposal) => {
    setImplementationPending(proposal.proposal_id);
    try {
      const updated = await requestProposalImplementation(proposal.proposal_id);
      setProposals((current) => current.map((item) => item.proposal_id === updated.proposal_id ? updated : item));
      setEvents(await getEvents());
      markProposalChanged(updated.proposal_id);
      setError(null);
    } catch (err) {
      setError(String(err));
    } finally {
      setImplementationPending(null);
    }
  };

  const handleCompleteImplementation = async (proposal: Proposal) => {
    setImplementationPending(proposal.proposal_id);
    try {
      const updated = await completeProposalImplementation(proposal.proposal_id);
      setProposals((current) => current.map((item) => item.proposal_id === updated.proposal_id ? updated : item));
      setEvents(await getEvents());
      markProposalChanged(updated.proposal_id);
      setError(null);
    } catch (err) {
      setError(String(err));
    } finally {
      setImplementationPending(null);
    }
  };

  const handleReviewImplementation = async (proposal: Proposal, reviewDecision: "accept" | "reject") => {
    setImplementationPending(proposal.proposal_id);
    try {
      const updated = await reviewProposalImplementation(proposal.proposal_id, reviewDecision);
      setProposals((current) => current.map((item) => item.proposal_id === updated.proposal_id ? updated : item));
      setEvents(await getEvents());
      markProposalChanged(updated.proposal_id);
      setError(null);
    } catch (err) {
      setError(String(err));
    } finally {
      setImplementationPending(null);
    }
  };

  const sortedEvents = [...events].sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  const latestEventBySource = new Map<string, Event>();
  for (const event of sortedEvents) {
    if (!latestEventBySource.has(event.source_id)) {
      latestEventBySource.set(event.source_id, event);
    }
  }
  const agentById = new Map(agents.map((agent) => [agent.id, agent]));

  const latestEventForAgent = (agent: Agent) => {
    return latestEventBySource.get(agent.id)
      ?? sortedEvents.find((event) => event.expedition_id === agent.current_assignment);
  };
  const latestEventForExpedition = (expedition: Expedition) => {
    return sortedEvents.find((event) => event.expedition_id === expedition.id);
  };

  const littleGuys = agents.filter((agent) => agent.allowed_as_little_guy);
  const visibleLittleGuys = littleGuys.filter((agent) => agent.room);
  const operationalSystems = agents.filter((agent) => !agent.allowed_as_little_guy);
  const reviewEvents = sortedEvents.filter((event) => event.needs_review || event.review_flags?.length || event.xp_claim_status === "review_pending" || ["medium", "high"].includes(event.risk_level) || event.status === "blocked");
  const openIncidents = incidents.filter((incident) => incident.status === "open");
  const stateCounts = countByState(agents, incidents);
  const currentSeasonSummary = currentSeasonState?.summary ?? seasonSummaries.find((summary) => !summary.ended_at) ?? seasonSummaries[0];
  const totalAwardedXp = currentSeasonSummary?.total_awarded_xp ?? events.reduce((sum, event) => sum + (event.awarded_xp ?? event.xp), 0);
  const totalBaseXp = currentSeasonSummary?.total_base_xp ?? events.reduce((sum, event) => sum + (event.base_xp ?? 0), 0);
  const totalActiveMinutes = currentSeasonSummary?.total_active_minutes ?? events.reduce((sum, event) => sum + (event.active_minutes ?? 0), 0);
  const averageMultiplier = currentSeasonSummary?.average_multiplier ?? (totalBaseXp ? totalAwardedXp / totalBaseXp : 0);
  const currentSeason = currentSeasonState?.season ?? currentSeasonSummary?.season ?? health?.xp_season ?? "0.1";
  const xpLabel = currentSeasonState?.label ?? currentSeasonSummary?.label ?? health?.xp_label ?? "Season 0.x - Uncapped Calibration XP";
  const nextSeasonReset = currentSeasonState?.next_reset_at ?? health?.season_window?.next_reset_at;
  const activeExpeditions = expeditions.filter((expedition) => expedition.progress_percent < 100 && expedition.status !== "complete");
  const recentFieldReports = sortedEvents.slice(0, 4);

  return (
    <main className="app-shell">
      <section className="observatory-banner">
        <div>
          <strong>Read-only Observatory Mode</strong>
          <span>No controls, no tunnel changes, no token rotation, no external sends, no memory mutation.</span>
        </div>
        <div className={`health-panel ${health?.ok ? "health-connected" : "health-disconnected"}`}>
          <span className="state-dot" />
          <div>
            <strong>{health?.ok ? "API connected" : "API disconnected"}</strong>
            <span>{health ? `${health.mutation_policy} / local writes ${health.local_writes_allowed === false ? "off" : "on"}` : "local API unavailable"}</span>
            {lastUpdated && <span>last observed {lastUpdated} / refresh {dashboardConfig?.refresh_seconds ?? 15}s</span>}
          </div>
        </div>
      </section>

      <header className="page-header living-header">
        <div>
          <p className="eyebrow">Local-first / Read-only / Expedition HQ</p>
          <h1>Living Expedition HQ</h1>
          <p>
            {xpLabel} keeps progress tied to active contribution time while the HQ remains a local read-only observatory.
          </p>
        </div>
        <div className="metric-grid" aria-label="Expedition HQ totals">
          <div><strong>{currentSeason}</strong><span>current season</span></div>
          <div><strong>{formatMinutes(totalActiveMinutes)}</strong><span>active time</span></div>
          <div><strong>{formatXp(totalBaseXp)}</strong><span>base XP</span></div>
          <div><strong>{formatXp(totalAwardedXp)}</strong><span>awarded XP</span></div>
          <div><strong>{averageMultiplier.toFixed(1)}x</strong><span>average multiplier</span></div>
          <div><strong>{formatShortDateTime(nextSeasonReset)}</strong><span>next 6am reset</span></div>
        </div>
      </header>

      <nav className="tabs" aria-label="Expedition HQ sections">
        {tabs.map((tab) => (
          <button
            className={activeTab === tab.id ? "active" : ""}
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {loading && <section className="notice">Loading local Expedition HQ data.</section>}
      {error && <section className="alert">API not reachable: {error}</section>}

      {activeTab === "hq" && (
        <div className="tab-page">
          <section className="today-panel">
            <div>
              <p className="eyebrow">Today at Expedition HQ</p>
              <h2>What are the little AI guys doing?</h2>
              <p>
                {visibleLittleGuys.length} specialists are visible in the base. {activeExpeditions.length} expeditions are still moving,{" "}
                {reviewEvents.length + openIncidents.length} items need human review, and {formatXp(totalAwardedXp)} uncapped calibration XP has been logged from {formatMinutes(totalActiveMinutes)} of active work.
              </p>
            </div>
            <div className="state-summary" aria-label="Current operational states">
              {stateCounts.map(({ state, count }) => (
                <div className={`state-chip state-${state}`} key={state}>
                  <span className="state-dot" />
                  <strong>{count}</strong>
                  <span>{state.replace("_", " ")}</span>
                </div>
              ))}
            </div>
          </section>

          <AgentXpBoard agents={littleGuys} />

          <HQRooms
            agents={agents}
            incidents={incidents}
            latestEventForAgent={latestEventForAgent}
            reviewEvents={reviewEvents}
            rooms={rooms}
            routeEdges={routeEdges}
          />

          <div className="living-grid">
            <CurrentActivity agents={agents} latestEventForAgent={latestEventForAgent} />
            <ReviewDesk events={sortedEvents} incidents={incidents} agentById={agentById} />
          </div>

          <section className="living-section">
            <SectionHeader eyebrow="Expedition Board" title="Active Expeditions" note="Compact view; full list lives in the Expeditions tab." />
            <div className="grid compact">
              {activeExpeditions.length
                ? activeExpeditions.slice(0, 3).map((expedition) => (
                  <ExpeditionCard
                    agentById={agentById}
                    key={expedition.id}
                    expedition={expedition}
                    latestEvent={latestEventForExpedition(expedition)}
                  />
                ))
                : <EmptyState label="No active expeditions are available from the local API." />}
            </div>
          </section>

          <section className="living-section">
            <SectionHeader eyebrow="Story Feed" title="Recent Field Reports" note="Newest reports from the local event ledger." />
            <div className="field-report-feed">
              {recentFieldReports.length
                ? recentFieldReports.map((event) => <FieldReportCard key={event.id} event={event} source={agentById.get(event.source_id)} />)
                : <EmptyState label="No field reports are available from the local event ledger." />}
            </div>
          </section>

          <section className="living-section calibration-log">
            <SectionHeader eyebrow="Season Log" title="Calibration Log" note={xpLabel} />
            <div className="calibration-grid">
              <p>XP resets run on the 6am local Season 0.x window; they reset current-season XP display/state only.</p>
              <p>Windows Task Scheduler is the reset source of truth; Codex automation only audits and reports scheduler state.</p>
              <p>Historical events, expedition records, milestones, badges, achievements, artifacts, and season summaries are preserved for comparison.</p>
              <p>The formulas are frozen during the test window unless August explicitly asks for a formula change.</p>
              <p>Current window: {currentSeasonState?.started_at ? formatShortDateTime(currentSeasonState.started_at) : "not set"} to {formatShortDateTime(nextSeasonReset)}.</p>
              <p>Season 0.x data will be used to balance later scoring, including future proposal wager ranges.</p>
            </div>
          </section>

          <TrophyShelf milestones={milestones} artifacts={artifacts} />
        </div>
      )}

      {activeTab === "expeditions" && (
        <div className="tab-page">
          <SectionHeader eyebrow="Expedition Board" title="All Expeditions" note={`${expeditions.length} local records`} />
          <div className="grid">
            {expeditions.length
              ? expeditions.map((expedition) => (
                <ExpeditionCard
                  agentById={agentById}
                  key={expedition.id}
                  expedition={expedition}
                  latestEvent={latestEventForExpedition(expedition)}
                />
              ))
              : <EmptyState label="No expeditions are available from the local API." />}
          </div>
        </div>
      )}

      {activeTab === "field-reports" && (
        <div className="tab-page">
          <SectionHeader eyebrow="Local Event Ledger" title="Field Reports" note={`${events.length} reports`} />
          <div className="field-report-feed full-feed">
            {sortedEvents.length
              ? sortedEvents.map((event) => <FieldReportCard key={event.id} event={event} source={agentById.get(event.source_id)} />)
              : <EmptyState label="No field reports are available from the local event ledger." />}
          </div>
        </div>
      )}

      {activeTab === "proposal-desk" && (
        <ProposalDeskView
          proposals={proposals}
          onDecision={openDecisionDialog}
          onStartWork={handleStartProposalWork}
          onRequestImplementation={handleRequestImplementation}
          onCompleteImplementation={handleCompleteImplementation}
          onReviewImplementation={handleReviewImplementation}
          decisionPending={decisionPending}
          workPending={workPending}
          implementationPending={implementationPending}
          agentById={agentById}
          currentSeason={currentSeasonState}
          recentlyFocusedProposalId={recentlyFocusedProposalId}
        />
      )}

      {pendingDecision && (
        <DecisionDialog
          proposal={pendingDecision.proposal}
          decision={pendingDecision.decision}
          note={decisionNoteDraft}
          onNoteChange={setDecisionNoteDraft}
          onCancel={closeDecisionDialog}
          onSubmit={submitProposalDecision}
          isSubmitting={decisionPending === pendingDecision.proposal.proposal_id}
        />
      )}

      {activeTab === "roster" && (
        <div className="tab-page">
          <SectionHeader eyebrow="Roster" title="Specialists And Constructs" note="Full roster moved off the main HQ floor." />
          <div className="grid compact">
            {[...littleGuys, ...operationalSystems].map((agent) => (
              <AgentCard key={agent.id} agent={agent} latestEvent={latestEventForAgent(agent)} />
            ))}
          </div>
        </div>
      )}

      {activeTab === "systems" && (
        <SystemsView
          routes={routes}
          memoryStores={memoryStores}
          incidents={incidents}
          plannedItems={plannedItems}
          artifacts={artifacts}
        />
      )}
    </main>
  );
}
