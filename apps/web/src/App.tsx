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
import { ExpeditionCard } from "./components/ExpeditionCard";
import { EventRow } from "./components/EventRow";

const visibleStates = ["awake", "on_call", "dormant", "blocked", "test_mode", "temporary_route"];
const roomOrder = ["central-desk", "archive-vault", "engineering-bay", "comms-wing", "systems-deck", "map-room"];
const roomLabel: Record<string, string> = {
  "central-desk": "Central Desk",
  "archive-vault": "Archive Vault",
  "engineering-bay": "Engineering Bay",
  "comms-wing": "Comms Wing",
  "systems-deck": "Systems Deck",
  "map-room": "Map Room"
};

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

export default function App() {
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

  const latestEventForAgent = (agent: Agent) => {
    return latestEventBySource.get(agent.id)
      ?? sortedEvents.find((event) => event.expedition_id === agent.current_assignment);
  };

  const littleGuys = agents;
  const operationalSystems = agents.filter((agent) => !agent.allowed_as_little_guy);
  const openIncidents = incidents.filter((incident) => incident.status === "open");
  const stateCounts = countByState(agents, incidents);
  const totalXp = events.reduce((sum, event) => sum + event.xp, 0);

  return (
    <main>
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

      <header className="page-header">
        <div>
          <p className="eyebrow">Local-first / Read-only / Expedition HQ</p>
          <h1>What are the little AI guys doing?</h1>
          <p>
            Observe specialists, constructs, routes, expeditions, field reports, and milestones without controlling live systems.
          </p>
        </div>
        <div className="metric-grid" aria-label="Expedition HQ totals">
          <div><strong>{agents.length}</strong><span>systems</span></div>
          <div><strong>{expeditions.length}</strong><span>expeditions</span></div>
          <div><strong>{events.length}</strong><span>field reports</span></div>
          <div><strong>{totalXp}</strong><span>earned XP</span></div>
        </div>
      </header>

      {loading && <section className="notice">Loading local Expedition HQ data.</section>}
      {error && <section className="alert">API not reachable: {error}</section>}

      <section>
        <h2>Bureau HQ</h2>
        <div className="state-summary" aria-label="Current operational states">
          {stateCounts.map(({ state, count }) => (
            <div className={`state-chip state-${state}`} key={state}>
              <span className="state-dot" />
              <strong>{count}</strong>
              <span>{state.replace("_", " ")}</span>
            </div>
          ))}
        </div>
        <div className="room-grid">
          {roomOrder.map((room) => {
            const roomAgents = littleGuys.filter((agent) => agent.room === room);
            return (
              <article className="room-band" key={room}>
                <header>
                  <h3>{roomLabel[room]}</h3>
                  <span>{roomAgents.length} assigned</span>
                </header>
                <div className="room-agents">
                  {roomAgents.length
                    ? roomAgents.map((agent) => <AgentCard key={agent.id} agent={agent} latestEvent={latestEventForAgent(agent)} />)
                    : <EmptyState label="No little AI guy assigned to this room." />}
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section>
        <h2>Expedition Board</h2>
        <div className="grid">
          {expeditions.length
            ? expeditions.map((expedition) => <ExpeditionCard key={expedition.id} expedition={expedition} />)
            : <EmptyState label="No expeditions are available from the local API." />}
        </div>
      </section>

      <section>
        <h2>Specialist Roster</h2>
        <div className="grid compact">
          {operationalSystems.length
            ? operationalSystems.map((agent) => <AgentCard key={agent.id} agent={agent} latestEvent={latestEventForAgent(agent)} />)
            : <EmptyState label="No constructs, routes, stations, or interfaces are available." />}
        </div>
      </section>

      <section>
        <h2>Field Reports</h2>
        <ul className="events">
          {events.length
            ? sortedEvents.map((event) => <EventRow key={event.id} event={event} />)
            : <EmptyState label="No field reports are available from the local event ledger." />}
        </ul>
      </section>

      <section>
        <h2>Milestone Gallery</h2>
        <div className="grid compact">
          {milestones.map((milestone) => (
            <article className="card" key={milestone.id}>
              <h3>{milestone.name}</h3>
              <p>{milestone.description}</p>
              <p className="muted">{milestone.status} / {milestone.xp_reward} XP</p>
            </article>
          ))}
          {artifacts.map((artifact) => (
            <article className="card artifact" key={artifact.id}>
              <h3>{artifact.title}</h3>
              <p>{artifact.summary}</p>
              <p className="muted">{artifact.artifact_type} / {artifact.path}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2>Routes And Archives</h2>
        <div className="split-grid">
          <div>
            <h3>Route Watch</h3>
            <div className="stack">
              {routes.map((route) => (
                <article className={`card route route-${route.status}`} key={route.id}>
                  <h4>{route.id}</h4>
                  <p>{route.route}</p>
                  <p className="muted">{route.status}</p>
                  {route.risk && <p className="risk">{route.risk}</p>}
                </article>
              ))}
            </div>
          </div>
          <div>
            <h3>Archive Vault</h3>
            <div className="stack">
              {memoryStores.map((store) => (
                <article className="card archive" key={store.id}>
                  <h4>{store.id}</h4>
                  <p>{store.classification}</p>
                  {store.path && <p className="muted">{store.path}</p>}
                  {store.notes && <p className="risk">{store.notes}</p>}
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section>
        <h2>Incidents And Blueprints</h2>
        <div className="split-grid">
          <div>
            <h3>Open Incidents</h3>
            <div className="stack">
              {openIncidents.map((incident) => (
                <article className="card incident" key={incident.id}>
                  <h4>{incident.id}</h4>
                  <p>{incident.summary}</p>
                  {incident.impact && <p className="risk">{incident.impact}</p>}
                </article>
              ))}
            </div>
          </div>
          <div>
            <h3>Planned Work</h3>
            <div className="stack">
              {plannedItems.map((item) => (
                <article className="card blueprint" key={item.id}>
                  <h4>{item.id}</h4>
                  <p>{item.classification}</p>
                  <p className="muted">{item.status}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
