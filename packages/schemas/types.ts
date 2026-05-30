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
  candidate_profile?: CandidateProfile;
}

export interface CandidateProfile {
  provider?: string;
  visiting_specialist?: boolean;
  free_tier_capabilities_profiled?: boolean;
  trust_level?: string;
  quality_band?: string;
  promotion_gate?: string;
  promotion_level?: string;
  trust_ladder?: string[];
  allowed_roles?: string[];
  restrictions?: string[];
  safety_flags?: string[];
  useful_output_count?: number;
  evidence_refs?: string[];
  availability_notes?: string;
  cost_quota_notes?: string;
  promotion_review_cadence?: string;
  promotion_recommendation?: string;
  promotion_dossier?: {
    pros: string[];
    cons: string[];
    recommendation: string;
    next_gate: string;
    evidence: string[];
  };
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

export interface RoomSeed {
  id: string;
  name: string;
  token: string;
  tone: string;
  role: string;
  visual_class: "room";
  sort_order: number;
}

export interface RouteEdgeSeed {
  id: string;
  from_node_id: string;
  to_node_id: string;
  route_type: string;
  status: string;
  privacy_class: string;
  risk_level: string;
  label: string;
  related_route_id?: string;
  summary: string;
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

export interface SeasonPolicySeed {
  season_family: string;
  first_season: string;
  formula_version: string;
  xp_mode: string;
  label: string;
  timezone: string;
  daily_reset_time: string;
  pre_restart_started_at: string;
  initial_restart_at: string;
  reset_mode: "display_current_season_only";
  scheduler_source_of_truth: "windows_task_scheduler";
  codex_automation_role: "audit_report_only";
  affected_domains: string[];
  preserve: string[];
  notes: string[];
}

export type ProposalStatus =
  | "draft"
  | "pending"
  | "approved"
  | "in_progress"
  | "implementation_requested"
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

export type ProposalDialogueMessageType =
  | "decision_note"
  | "clarification_question"
  | "user_reply"
  | "agent_revision_note"
  | "work_start"
  | "implementation_request"
  | "implementation_complete"
  | "implementation_review";

export interface ProposalDialogueMessageSeed {
  message_id: string;
  proposal_id: string;
  author_type: "user" | "agent" | "system";
  author_id: string;
  message: string;
  created_at: string;
  message_type: ProposalDialogueMessageType;
}

export type ProposalVoteValue = "support" | "oppose" | "abstain";

export interface ProposalVoteSeed {
  vote_id: string;
  proposal_id: string;
  agent_id: string;
  vote: ProposalVoteValue;
  confidence: number;
  reasoning: string;
  expected_benefit: string;
  expected_failure_mode: string;
  risk_notes: string;
  context_notes?: string;
  created_at: string;
  usefulness_status: "pending_outcome" | "useful" | "not_useful" | "not_awarded";
  peer_review_xp: number;
  response_kind?: "recorded" | "required_abstain" | "amended_after_prompt";
  peer_review_xp_multiplier?: number;
  peer_review_xp_penalty_reason?: string;
  agent_memory_note?: string;
}

export interface ProposalCouncilSummary {
  eligible_count: number;
  participation_count: number;
  participation_rate: number;
  peer_review_participation_count?: number;
  peer_review_participation_rate?: number;
  amendment_requested_count?: number;
  vote_counts: Record<ProposalVoteValue, number>;
  average_confidence_by_vote: Record<ProposalVoteValue, number>;
  healthy_abstain_count: number;
  peer_review_xp_awarded: number;
  useful_assessment_count: number;
  pending_assessment_count: number;
  guidance: string;
}

export interface ProposalImplementationRoutePlan {
  orchestration_layer?: string;
  route_snapshot_version?: string;
  authority_source?: string;
  autonomy_scope?: string;
  dispatch_mode?: string;
  dispatch_status?: string;
  routing_owner?: string;
  primary_provider?: string;
  privacy?: string;
  risk?: string;
  task_type?: string;
  policy_basis?: string;
  provider_roles?: string[];
  selected_agents?: RouteParticipant[];
  candidate_providers?: RouteParticipant[];
  skipped_providers?: RouteParticipant[];
  provider_result_refs?: string[];
  token_saving_choices?: string[];
  promotion_policy?: string;
  dispatch_job_path?: string;
  dispatch_run_dir?: string;
  recommended_agents?: {
    agent_id: string;
    role: string;
    reason: string;
  }[];
  affected_areas?: string[];
  approval_required_for?: string[];
  final_reviewer_id?: string;
}

export interface RouteParticipant {
  agent_id: string;
  provider?: string;
  access_mode?: string;
  trust_level?: string;
  task_role?: string;
  route_status?: string;
  cost_quota_notes?: string;
  unavailable_reason?: string;
  reason?: string;
  result_refs?: string[];
  evidence_refs?: string[];
  capabilities?: string[];
}

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
  broadcast_status?: string;
  broadcasted_at?: string | null;
  eligible_agent_ids?: string[];
  council_votes?: ProposalVoteSeed[];
  council_summary?: ProposalCouncilSummary;
  decision: "approve" | "deny" | "revise" | "defer" | null;
  decision_note: string | null;
  decision_note_provided?: boolean;
  decided_at: string | null;
  work_started_at?: string | null;
  work_start_note?: string | null;
  work_start_note_provided?: boolean;
  implementation_session_id?: string | null;
  implementation_requested_at?: string | null;
  implementation_request_note?: string | null;
  implementation_request_note_provided?: boolean;
  implementation_brief_path?: string | null;
  implementation_dispatch_status?: string | null;
  implementation_route_plan?: ProposalImplementationRoutePlan;
  implementation_completed_at?: string | null;
  implementation_completion_note?: string | null;
  implementation_evidence_refs?: string[];
  implementation_reviewed_at?: string | null;
  implementation_review_note?: string | null;
  implementation_reviewer_id?: string | null;
  simulated_xp_gain: number;
  simulated_xp_loss: number;
  dialogue_messages?: ProposalDialogueMessageSeed[];
  is_test_proposal?: boolean;
  expected_decision?: "approve" | "deny" | "revise" | "defer" | null;
  excluded_from_reputation?: boolean;
  created_at: string;
  updated_at: string;
}
