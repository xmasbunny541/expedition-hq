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
  xp_season: string;
  formula_version: string;
  xp_mode: string;
  active_minutes: number;
  base_xp: number;
  awarded_xp: number;
  xp: number;
  total_multiplier_raw: number;
  multiplier_cap: number | null;
  xp_source: string;
  xp_confidence: string;
  party_agents: string[];
  party_size: number;
  scoring_multipliers: ScoringMultipliers;
  shadow_multipliers: ShadowMultipliers;
  shadow_multiplier_notes: string[] | string;
  multiplier_notes: string[] | string;
  scaling_flags: string[];
  tags: string[];
}

export interface ScoringMultipliers {
  grinding: number;
  party_size: number;
  artifact: number;
  blocker_break: number;
  reuse_leverage: number;
  risk_control: number;
}

export interface ShadowMultipliers {
  discovery: boolean;
  handoff_chain: boolean;
  polish: boolean;
  sentimental_record: boolean;
}

export interface ShadowMultiplierCounts {
  discovery: number;
  handoff_chain: number;
  polish: number;
  sentimental_record: number;
}

export interface SeasonSummarySeed {
  season: string;
  formula_version: string;
  xp_mode: string;
  label: string;
  started_at: string;
  ended_at: string | null;
  total_active_minutes: number;
  total_base_xp: number;
  total_awarded_xp: number;
  average_multiplier: number;
  event_count: number;
  field_report_count: number;
  artifact_count: number;
  review_item_count: number;
  average_party_size: number;
  average_party_multiplier: number;
  average_grinding_multiplier: number;
  most_common_scoring_multiplier_sources: { source: string; count: number }[];
  shadow_multiplier_counts: ShadowMultiplierCounts;
  top_agents_by_base_xp: { agent_id: string; xp: number }[];
  top_agents_by_awarded_xp: { agent_id: string; xp: number }[];
  top_expeditions_by_base_xp: { expedition_id: string; xp: number }[];
  top_expeditions_by_awarded_xp: { expedition_id: string; xp: number }[];
  notes: string[];
}

export type ProposalStatus =
  | "draft"
  | "pending"
  | "approved"
  | "denied"
  | "revise_requested"
  | "deferred"
  | "implemented"
  | "accepted"
  | "rejected"
  | "archived";

export type ProposalType =
  | "polish"
  | "discovery"
  | "sentimental_record"
  | "handoff_workflow"
  | "gamification"
  | "safety"
  | "architecture";

export interface ProposalSeed {
  proposal_id: string;
  xp_season: string;
  formula_version: string;
  source_agent: string;
  proposal_type: ProposalType;
  title: string;
  summary: string;
  reasoning: string;
  estimated_active_minutes: number;
  requested_xp_wager: number;
  confidence: number;
  risk_level: string;
  affected_areas: string[];
  acceptance_criteria: string[];
  rollback_plan: string;
  status: ProposalStatus;
  decision: "approve" | "deny" | "revise" | "defer" | null;
  decision_note: string | null;
  decided_at: string | null;
  simulated_xp_gain: number;
  simulated_xp_loss: number;
  created_at: string;
  updated_at: string;
}
