import type { Agent, Event, Incident, Room, RouteEdge } from "../types";
import { displayName, VisualToken } from "./VisualToken";

function roomState(occupants: Agent[], reviewCount: number) {
  if (reviewCount > 0 || occupants.some((agent) => agent.ui_state === "blocked" || agent.status.includes("blocked"))) {
    return "Needs Review";
  }
  if (occupants.some((agent) => agent.ui_state === "awake")) return "Awake";
  if (occupants.some((agent) => agent.ui_state === "on_call" || agent.ui_state === "test_mode")) return "On Call";
  if (occupants.length > 0) return "Quiet";
  return "Unassigned";
}

function latestActivity(occupants: Agent[], latestEventForAgent: (agent: Agent) => Event | undefined) {
  for (const occupant of occupants) {
    const latest = latestEventForAgent(occupant);
    if (latest) return latest.title;
  }
  return "No recent activity recorded.";
}

export function HQRooms({
  agents,
  incidents,
  latestEventForAgent,
  reviewEvents,
  rooms,
  routeEdges
}: {
  agents: Agent[];
  incidents: Incident[];
  latestEventForAgent: (agent: Agent) => Event | undefined;
  reviewEvents: Event[];
  rooms: Room[];
  routeEdges: RouteEdge[];
}) {
  const sortedRooms = [...rooms].sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0));
  return (
    <section className="living-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Living HQ</p>
          <h2>HQ Rooms</h2>
        </div>
        <span className="section-note">Read-only room state from seed data, route edges, and event history.</span>
      </div>

      <div className="room-map" aria-label="Expedition HQ rooms">
        {sortedRooms.map((room) => {
          const roomAgents = agents.filter((agent) => agent.room === room.id);
          const reviewCount = room.id === "review-desk"
            ? reviewEvents.length + incidents.filter((incident) => incident.status === "open").length
            : 0;
          const occupants = room.id === "review-desk"
            ? agents.filter((agent) => reviewEvents.some((event) => event.source_id === agent.id)).slice(0, 3)
            : roomAgents.slice(0, 3);
          const assignedCount = room.id === "review-desk" ? reviewCount : roomAgents.length;
          const state = roomState(roomAgents, reviewCount);
          const activity = room.id === "review-desk"
            ? reviewEvents[0]?.title ?? incidents.find((incident) => incident.status === "open")?.summary ?? "No review queue items."
            : latestActivity(roomAgents, latestEventForAgent);

          return (
            <article className={`room-panel room-${room.tone}`} key={room.id}>
              <header className="room-panel-header">
                <VisualToken label={room.token} kind="room" state={state.toLowerCase().replace(" ", "_")} />
                <div>
                  <h3>{room.name}</h3>
                  <span>{assignedCount} observed</span>
                </div>
              </header>
              <p className="room-state">{state}</p>
              {room.role && <p className="room-role">{room.role}</p>}
              <p className="room-activity">{activity}</p>
              <div className="room-occupants">
                {occupants.length ? occupants.map((agent) => (
                  <span className="occupant-chip" key={agent.id}>
                    <VisualToken agent={agent} size="small" />
                    <span>{displayName(agent)}</span>
                  </span>
                )) : (
                  <span className="occupant-chip muted">No occupant assigned</span>
                )}
              </div>
            </article>
          );
        })}
      </div>

      {routeEdges.length > 0 && (
        <div className="route-graph" aria-label="Room route edges">
          {routeEdges.map((edge) => (
            <article className={`route-edge state-${edge.status} risk-${edge.risk_level ?? "low"}`} key={edge.id}>
              <span>{edge.from_node_id.replace(/-/g, " ")}</span>
              <strong>{edge.label ?? edge.route_type.replace(/_/g, " ")}</strong>
              <span>{edge.to_node_id.replace(/-/g, " ")}</span>
              <p>{edge.summary}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
