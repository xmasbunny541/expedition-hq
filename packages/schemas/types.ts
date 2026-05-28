export type VisualClass =
  | "specialist"
  | "candidate_specialist"
  | "construct"
  | "automation"
  | "route_bridge"
  | "interface"
  | "station"
  | "archive"
  | "data_source"
  | "planned_blueprint"
  | "unknown";

export type UIState =
  | "awake"
  | "on_call"
  | "dormant"
  | "test_mode"
  | "temporary_route"
  | "working_local"
  | "fragile_link"
  | "stable"
  | "sleeping"
  | "blueprint"
  | "blocked"
  | "experimental"
  | "unknown";

export interface AgentSeed {
  id: string;
  display_name: string;
  visual_name: string;
  source_classification: string;
  visual_class: VisualClass;
  status: string;
  ui_state: UIState;
  visual_archetype: string;
  room: string;
  current_assignment: string | null;
  summary: string;
  decision_mode: string;
  needs_august_review: string;
  logs_history: boolean | string;
  allowed_as_little_guy: boolean;
  capabilities: string[];
  triggers: string[];
  tools_or_systems: string[];
}

export interface ExpeditionSeed {
  id: string;
  name: string;
  status: string;
  summary: string;
  campaign: string;
  priority: string;
  progress_percent: number;
  assigned_specialists: string[];
  next_objective: string;
}

export interface EventSeed {
  id: string;
  timestamp: string;
  source_id: string;
  expedition_id?: string;
  event_type: string;
  title: string;
  summary: string;
  status: string;
  risk_level: string;
  needs_review: boolean;
  xp: number;
  tags: string[];
}
