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
  Route,
  SeasonSummary
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8789";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
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
