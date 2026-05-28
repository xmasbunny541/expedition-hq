export interface Agent {
  id: string;
  display_name: string;
  visual_name?: string;
  visual_class: string;
  status: string;
  ui_state: string;
  visual_archetype?: string;
  room?: string;
  current_assignment: string | null;
  summary?: string;
  allowed_as_little_guy: boolean;
}

export interface Expedition {
  id: string;
  name: string;
  status: string;
  summary: string;
  progress_percent: number;
  assigned_specialists: string[];
  next_objective: string;
}

export interface Event {
  id: string;
  timestamp: string;
  source_id: string;
  expedition_id?: string | null;
  event_type: string;
  title: string;
  summary: string;
  status: string;
  risk_level: string;
  needs_review: boolean;
  xp: number;
  tags: string[];
}

export interface Milestone {
  id: string;
  name: string;
  description: string;
  status: string;
  xp_reward: number;
  unlock_condition: string;
}

export interface Incident {
  id: string;
  summary: string;
  impact?: string;
  status: string;
}

export interface Route {
  id: string;
  route: string;
  status: string;
  risk?: string;
}

export interface MemoryStore {
  id: string;
  classification: string;
  path?: string;
  contents?: string[];
  notes?: string;
}

export interface PlannedItem {
  id: string;
  classification: string;
  status: string;
  required_before_activation?: string[];
}

export interface Artifact {
  id: string;
  title: string;
  artifact_type: string;
  path: string;
  summary?: string;
}

export interface Health {
  ok: boolean;
  service: string;
  mode: string;
  mutation_policy: string;
}
