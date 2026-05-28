import { useEffect, useState } from "react";
import {
  decideProposal,
  getAgents,
  getArtifacts,
  getEvents,
  getExpeditions,
  getHealth,
  getIncidents,
  getMemoryStores,
  getMilestones,
  getPlannedItems,
  getProposals,
  getRoutes,
  getSeasonSummaries
} from "./api";
import type {
  Agent,
  Artifact,
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
  SeasonSummary
} from "./types";
import { AgentCard } from "./components/AgentCard";
import { CurrentActivity } from "./components/CurrentActivity";
import { ExpeditionCard } from "./components/ExpeditionCard";
import { FieldReportCard } from "./components/FieldReportCard";
import { HQRooms } from "./components/HQRooms";
import { ReviewDesk } from "./components/ReviewDesk";
import { TrophyShelf } from "./components/TrophyShelf";
import { VisualToken } from "./components/VisualToken";

type TabId = "hq" | "expeditions" | "field-reports" | "proposal-desk" | "roster" | "systems";

const tabs: { id: TabId; label: string }[] = [
  { id: "hq", label: "HQ" },
  { id: "expeditions", label: "Expeditions" },
  { id: "field-reports", label: "Field Reports" },
  { id: "proposal-desk", label: "Proposal Desk" },
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

function labelize(value: string) {
  return value.replace(/_/g, " ");
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

function ProposalAnalytics({ proposals }: { proposals: Proposal[] }) {
  const reputationProposals = proposals.filter((proposal) => !proposal.is_test_proposal && !proposal.excluded_from_reputation);
  const qaProposals = proposals.filter((proposal) => proposal.is_test_proposal || proposal.excluded_from_reputation);
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

  return (
    <section className="living-section proposal-analytics">
      <SectionHeader eyebrow="Proposal Analytics" title="Soft Wager Calibration" note="Normal analytics exclude QA-only denial probes." />
      <div className="proposal-metrics">
        <div><strong>{reputationProposals.length}</strong><span>normal proposals</span></div>
        <div><strong>{qaProposals.length}</strong><span>QA test proposals</span></div>
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
      <div className="proposal-breakdown-grid">
        <Breakdown title="Count By Type" counts={countsByType} />
        <Breakdown title="Decision And Status Counts" counts={countsByDecision} />
        <Breakdown title="Proposals By Agent" counts={countsByAgent} />
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
  decisionPending
}: {
  title: string;
  note: string;
  proposals: Proposal[];
  onDecision: (proposal: Proposal, decision: ProposalDecision) => void;
  decisionPending: string | null;
}) {
  return (
    <section className="living-section">
      <SectionHeader eyebrow="Proposal Desk" title={title} note={note} />
      <div className="proposal-grid">
        {proposals.length
          ? proposals.map((proposal) => (
            <ProposalCard
              key={proposal.proposal_id}
              proposal={proposal}
              onDecision={onDecision}
              decisionPending={decisionPending === proposal.proposal_id}
            />
          ))
          : <EmptyState label="No proposals in this section." />}
      </div>
    </section>
  );
}

function ProposalCard({
  proposal,
  onDecision,
  decisionPending
}: {
  proposal: Proposal;
  onDecision: (proposal: Proposal, decision: ProposalDecision) => void;
  decisionPending: boolean;
}) {
  const hasDecisionNote = Boolean(proposal.decision_note);
  const canDecide = proposal.status === "pending";
  const clarificationQuestions = (proposal.dialogue_messages ?? []).filter(
    (message) => message.message_type === "clarification_question"
  );
  return (
    <article className={`proposal-card risk-${proposal.risk_level}`} data-proposal-id={proposal.proposal_id}>
      <div className="proposal-card-header">
        <div>
          <p className="eyebrow">{labelize(proposal.proposal_type)}</p>
          <h3>{proposal.title}</h3>
          <p>{proposal.summary}</p>
        </div>
        <span className="badge">{labelize(proposal.status)}</span>
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
        <div><span>confidence</span><strong>{formatPercent(proposal.confidence)}</strong></div>
        <div><span>requested wager</span><strong>{formatXp(proposal.requested_xp_wager)} XP</strong></div>
        <div><span>estimated active time</span><strong>{formatMinutes(proposal.estimated_active_minutes)}</strong></div>
        <div><span>risk level</span><strong>{proposal.risk_level}</strong></div>
      </div>

      <p className="proposal-reasoning">{proposal.reasoning}</p>

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
    </article>
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
            <p className="eyebrow">Proposal Desk Decision</p>
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
          This records a local Proposal Desk decision only. It does not implement the proposal.
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
  decisionPending
}: {
  proposals: Proposal[];
  onDecision: (proposal: Proposal, decision: ProposalDecision) => void;
  decisionPending: string | null;
}) {
  const pending = proposals.filter((proposal) => ["draft", "pending", "revise_requested"].includes(proposal.status));
  const approved = proposals.filter((proposal) => ["approved", "implemented", "accepted"].includes(proposal.status));
  const denied = proposals.filter((proposal) => ["denied", "rejected"].includes(proposal.status));
  const deferred = proposals.filter((proposal) => ["deferred", "archived"].includes(proposal.status));

  return (
    <div className="tab-page proposal-desk-page">
      <section className="today-panel proposal-desk-intro">
        <div>
          <p className="eyebrow">Local-only Review</p>
          <h2>Proposal Desk</h2>
          <p>
            Subjective and directional ideas can be reviewed here before implementation. Soft wagers are recorded for
            Season 0.x calibration, but they never apply real XP or trigger work automatically.
          </p>
        </div>
        <div className="state-summary" aria-label="Proposal Desk safety posture">
          <div className="state-chip state-awake"><span className="state-dot" /><strong>local</strong><span>SQLite only</span></div>
          <div className="state-chip state-test_mode"><span className="state-dot" /><strong>soft</strong><span>wagers only</span></div>
          <div className="state-chip state-dormant"><span className="state-dot" /><strong>no</strong><span>auto implementation</span></div>
        </div>
      </section>

      <ProposalSection
        title="Pending Proposals"
        note={`${pending.length} awaiting decision or clarification`}
        proposals={pending}
        onDecision={onDecision}
        decisionPending={decisionPending}
      />
      <ProposalSection
        title="Approved Proposals"
        note={`${approved.length} eligible for future implementation planning`}
        proposals={approved}
        onDecision={onDecision}
        decisionPending={decisionPending}
      />
      <ProposalSection
        title="Denied Proposals"
        note={`${denied.length} recorded with simulated wager outcomes`}
        proposals={denied}
        onDecision={onDecision}
        decisionPending={decisionPending}
      />
      <ProposalSection
        title="Deferred Proposals"
        note={`${deferred.length} archived for later review`}
        proposals={deferred}
        onDecision={onDecision}
        decisionPending={decisionPending}
      />
      <ProposalAnalytics proposals={proposals} />
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
  const [memoryStores, setMemoryStores] = useState<MemoryStore[]>([]);
  const [plannedItems, setPlannedItems] = useState<PlannedItem[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [seasonSummaries, setSeasonSummaries] = useState<SeasonSummary[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [decisionPending, setDecisionPending] = useState<string | null>(null);
  const [pendingDecision, setPendingDecision] = useState<{ proposal: Proposal; decision: ProposalDecision } | null>(null);
  const [decisionNoteDraft, setDecisionNoteDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      getHealth(),
      getAgents(),
      getExpeditions(),
      getEvents(),
      getMilestones(),
      getIncidents(),
      getRoutes(),
      getMemoryStores(),
      getPlannedItems(),
      getArtifacts(),
      getSeasonSummaries(),
      getProposals()
    ])
      .then(([apiHealth, a, ex, ev, ms, inc, rt, mem, planned, art, summaries, prop]) => {
        setHealth(apiHealth);
        setAgents(a);
        setExpeditions(ex);
        setEvents(ev);
        setMilestones(ms);
        setIncidents(inc);
        setRoutes(rt);
        setMemoryStores(mem);
        setPlannedItems(planned);
        setArtifacts(art);
        setSeasonSummaries(summaries);
        setProposals(prop);
        setError(null);
      })
      .catch((err) => {
        setHealth(null);
        setError(String(err));
      })
      .finally(() => setLoading(false));
  }, []);

  const openDecisionDialog = (proposal: Proposal, decision: ProposalDecision) => {
    setPendingDecision({ proposal, decision });
    setDecisionNoteDraft("");
  };

  const closeDecisionDialog = () => {
    if (decisionPending) return;
    setPendingDecision(null);
    setDecisionNoteDraft("");
  };

  const submitProposalDecision = async () => {
    if (!pendingDecision) return;
    const { proposal, decision } = pendingDecision;
    setDecisionPending(proposal.proposal_id);
    try {
      const updated = await decideProposal(proposal.proposal_id, decision, decisionNoteDraft.trim());
      setProposals((current) => current.map((item) => item.proposal_id === updated.proposal_id ? updated : item));
      setEvents(await getEvents());
      setPendingDecision(null);
      setDecisionNoteDraft("");
      setError(null);
    } catch (err) {
      setError(String(err));
    } finally {
      setDecisionPending(null);
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

  const littleGuys = agents.filter((agent) => agent.allowed_as_little_guy);
  const spotlightLittleGuys = littleGuys.filter((agent) => [
    "openclaw-main",
    "codex-memory-operator",
    "home-windows-codex",
    "codex-headless-cli-runs"
  ].includes(agent.id));
  const operationalSystems = agents.filter((agent) => !agent.allowed_as_little_guy);
  const reviewEvents = sortedEvents.filter((event) => event.needs_review || ["medium", "high"].includes(event.risk_level) || event.status === "blocked");
  const openIncidents = incidents.filter((incident) => incident.status === "open");
  const stateCounts = countByState(agents, incidents);
  const currentSeasonSummary = seasonSummaries.find((summary) => !summary.ended_at) ?? seasonSummaries[0];
  const totalAwardedXp = currentSeasonSummary?.total_awarded_xp ?? events.reduce((sum, event) => sum + (event.awarded_xp ?? event.xp), 0);
  const totalBaseXp = currentSeasonSummary?.total_base_xp ?? events.reduce((sum, event) => sum + (event.base_xp ?? 0), 0);
  const totalActiveMinutes = currentSeasonSummary?.total_active_minutes ?? events.reduce((sum, event) => sum + (event.active_minutes ?? 0), 0);
  const averageMultiplier = currentSeasonSummary?.average_multiplier ?? (totalBaseXp ? totalAwardedXp / totalBaseXp : 0);
  const currentSeason = currentSeasonSummary?.season ?? health?.xp_season ?? "0.1";
  const xpLabel = currentSeasonSummary?.label ?? health?.xp_label ?? "Season 0.x · Uncapped Calibration XP";
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
            <span>{health ? health.mutation_policy : "local API unavailable"}</span>
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
                {spotlightLittleGuys.length} specialists are visible in the base. {activeExpeditions.length} expeditions are still moving,{" "}
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

          <HQRooms agents={agents} incidents={incidents} latestEventForAgent={latestEventForAgent} reviewEvents={reviewEvents} />

          <div className="living-grid">
            <CurrentActivity agents={agents} latestEventForAgent={latestEventForAgent} />
            <ReviewDesk events={sortedEvents} incidents={incidents} agentById={agentById} />
          </div>

          <section className="living-section">
            <SectionHeader eyebrow="Expedition Board" title="Active Expeditions" note="Compact view; full list lives in the Expeditions tab." />
            <div className="grid compact">
              {activeExpeditions.length
                ? activeExpeditions.slice(0, 3).map((expedition) => <ExpeditionCard key={expedition.id} expedition={expedition} />)
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
              <p>XP resets are expected during Season 0.x; they reset current-season display, not the event ledger.</p>
              <p>Historical events and season summaries are preserved so Season 0.1, 0.2, and later calibration windows can be compared.</p>
              <p>The formulas are frozen during the test window unless August explicitly asks for a formula change.</p>
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
              ? expeditions.map((expedition) => <ExpeditionCard key={expedition.id} expedition={expedition} />)
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
          decisionPending={decisionPending}
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
