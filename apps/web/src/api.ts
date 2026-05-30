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
  ProposalVote,
  Route,
  RouteEdge,
  Room,
  SeasonCurrent,
  SeasonParticipation,
  SeasonSummary
} from "./types";

const configuredApiBase = import.meta.env.VITE_API_BASE?.trim();
const API_BASE = (configuredApiBase || "http://127.0.0.1:8789").replace(/\/+$/, "");

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status} for ${path}`);
  return res.json();
}

async function patchJson<T>(path: string, payload: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`API error ${res.status} for ${path}`);
  return res.json();
}

export function getAgents() {
  return getJson<Agent[]>("/agents");
}

export function getHealth() {
  return getJson<Health>("/health");
}

export function getExpeditions() {
  return getJson<Expedition[]>("/expeditions");
}

export function getEvents() {
  return getJson<Event[]>("/events");
}

export function getMilestones() {
  return getJson<Milestone[]>("/milestones");
}

export function getIncidents() {
  return getJson<Incident[]>("/incidents");
}

export function getRoutes() {
  return getJson<Route[]>("/routes");
}

export function getRooms() {
  return getJson<Room[]>("/rooms");
}

export function getRouteEdges() {
  return getJson<RouteEdge[]>("/route-edges");
}

export function getDashboardConfig() {
  return getJson<DashboardConfig>("/dashboard-config");
}

export function getMemoryStores() {
  return getJson<MemoryStore[]>("/memory-stores");
}

export function getPlannedItems() {
  return getJson<PlannedItem[]>("/planned");
}

export function getArtifacts() {
  return getJson<Artifact[]>("/artifacts");
}

export function getSeasonSummaries() {
  return getJson<SeasonSummary[]>("/season-summaries");
}

export function getCurrentSeason() {
  return getJson<SeasonCurrent>("/season-current");
}

export function getSeasonParticipation() {
  return getJson<SeasonParticipation>("/season-participation");
}

export function getProposals() {
  return getJson<Proposal[]>("/proposals");
}

export function decideProposal(
  proposalId: string,
  decision: ProposalDecision,
  decisionNote?: string
) {
  return patchJson<Proposal>(`/proposals/${proposalId}/decision`, {
    decision,
    decision_note: decisionNote ?? ""
  });
}

export function startProposalWork(
  proposalId: string,
  startNote?: string
) {
  return patchJson<Proposal>(`/proposals/${proposalId}/work-start`, {
    start_note: startNote ?? ""
  });
}

export function requestProposalImplementation(
  proposalId: string,
  requestNote?: string
) {
  return patchJson<Proposal>(`/proposals/${proposalId}/implementation-request`, {
    request_note: requestNote ?? ""
  });
}

export function completeProposalImplementation(
  proposalId: string,
  completionNote?: string,
  evidenceRefs: string[] = []
) {
  return patchJson<Proposal>(`/proposals/${proposalId}/implementation-complete`, {
    completion_note: completionNote ?? "",
    evidence_refs: evidenceRefs
  });
}

export function reviewProposalImplementation(
  proposalId: string,
  reviewDecision: "accept" | "reject",
  reviewNote?: string
) {
  return patchJson<Proposal>(`/proposals/${proposalId}/implementation-review`, {
    review_decision: reviewDecision,
    review_note: reviewNote ?? "",
    reviewer_id: "august"
  });
}

export async function castProposalVote(
  proposalId: string,
  vote: Omit<
    ProposalVote,
    | "vote_id"
    | "proposal_id"
    | "created_at"
    | "usefulness_status"
    | "peer_review_xp"
    | "response_kind"
    | "peer_review_xp_multiplier"
    | "peer_review_xp_penalty_reason"
    | "agent_memory_note"
  > & {
    vote_id?: string;
  }
) {
  const res = await fetch(`${API_BASE}/proposals/${proposalId}/votes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(vote)
  });
  if (!res.ok) throw new Error(`API error ${res.status} for /proposals/${proposalId}/votes`);
  return res.json() as Promise<Proposal>;
}
