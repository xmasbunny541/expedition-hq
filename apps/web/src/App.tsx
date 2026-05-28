import { useEffect, useState } from "react";
import {
  getAgents,
  getArtifacts,
  getEvents,
  getExpeditions,
  getHealth,
  getIncidents,
  getMemoryStores,
  getMilestones,
  getPlannedItems,
  getRoutes
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
  Route
} from "./types";
import { AgentCard } from "./components/AgentCard";
import { CurrentActivity } from "./components/CurrentActivity";
import { ExpeditionCard } from "./components/ExpeditionCard";
import { FieldReportCard } from "./components/FieldReportCard";
import { HQRooms } from "./components/HQRooms";
import { ReviewDesk } from "./components/ReviewDesk";
import { TrophyShelf } from "./components/TrophyShelf";
import { VisualToken } from "./components/VisualToken";

type TabId = "hq" | "expeditions" | "field-reports" | "roster" | "systems";

const tabs: { id: TabId; label: string }[] = [
  { id: "hq", label: "HQ" },
  { id: "expeditions", label: "Expeditions" },
  { id: "field-reports", label: "Field Reports" },
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
      getArtifacts()
    ])
      .then(([apiHealth, a, ex, ev, ms, inc, rt, mem, planned, art]) => {
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
        setError(null);
      })
      .catch((err) => {
        setHealth(null);
        setError(String(err));
      })
      .finally(() => setLoading(false));
  }, []);

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
  const totalXp = events.reduce((sum, event) => sum + event.xp, 0);
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
            A cozy command room for watching specialists, constructs, routes, expeditions, field reports, and trophies without controlling live systems.
          </p>
        </div>
        <div className="metric-grid" aria-label="Expedition HQ totals">
          <div><strong>{spotlightLittleGuys.length}</strong><span>little specialists</span></div>
          <div><strong>{activeExpeditions.length}</strong><span>active expeditions</span></div>
          <div><strong>{reviewEvents.length + openIncidents.length}</strong><span>review items</span></div>
          <div><strong>{totalXp}</strong><span>earned XP</span></div>
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
                {reviewEvents.length + openIncidents.length} items need human review, and {totalXp} XP has been logged from real field reports.
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
