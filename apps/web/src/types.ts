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

export interface SeasonSummary {
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

export type ProposalDecision = "approve" | "deny" | "revise" | "defer";

export interface Proposal {
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
  decision: ProposalDecision | null;
  decision_note: string | null;
  decided_at: string | null;
  simulated_xp_gain: number;
  simulated_xp_loss: number;
  is_test_proposal?: boolean;
  expected_decision?: ProposalDecision | null;
  excluded_from_reputation?: boolean;
  created_at: string;
  updated_at: string;
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
  xp_season?: string;
  formula_version?: string;
  xp_mode?: string;
  xp_label?: string;
}
