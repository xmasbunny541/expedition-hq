PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  visual_name TEXT,
  source_classification TEXT,
  visual_class TEXT NOT NULL,
  status TEXT NOT NULL,
  ui_state TEXT NOT NULL,
  visual_archetype TEXT,
  room TEXT,
  current_assignment TEXT,
  summary TEXT,
  decision_mode TEXT,
  needs_august_review TEXT,
  logs_history TEXT,
  allowed_as_little_guy INTEGER DEFAULT 0,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS expeditions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  summary TEXT,
  campaign TEXT,
  priority TEXT,
  progress_percent INTEGER DEFAULT 0,
  next_objective TEXT,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL,
  source_id TEXT NOT NULL,
  expedition_id TEXT,
  event_type TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  status TEXT NOT NULL,
  risk_level TEXT,
  needs_review INTEGER DEFAULT 0,
  xp REAL DEFAULT 0,
  xp_season TEXT,
  formula_version TEXT,
  xp_mode TEXT,
  active_minutes REAL DEFAULT 0,
  base_xp REAL DEFAULT 0,
  awarded_xp REAL DEFAULT 0,
  total_multiplier_raw REAL DEFAULT 1,
  multiplier_cap REAL,
  xp_source TEXT,
  xp_confidence TEXT,
  party_agents_json TEXT DEFAULT '[]',
  party_size INTEGER DEFAULT 0,
  scoring_multipliers_json TEXT DEFAULT '{}',
  shadow_multipliers_json TEXT DEFAULT '{}',
  shadow_multiplier_notes_json TEXT DEFAULT '[]',
  multiplier_notes_json TEXT DEFAULT '[]',
  scaling_flags_json TEXT DEFAULT '[]',
  source_project TEXT,
  xp_claim_status TEXT DEFAULT 'calibration_awarded',
  evidence_refs_json TEXT DEFAULT '[]',
  artifact_refs_json TEXT DEFAULT '[]',
  field_report_path TEXT,
  review_flags_json TEXT DEFAULT '[]',
  tags_json TEXT DEFAULT '[]',
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS milestones (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT,
  xp_reward INTEGER DEFAULT 0,
  unlock_condition TEXT,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS incidents (
  id TEXT PRIMARY KEY,
  summary TEXT NOT NULL,
  impact TEXT,
  status TEXT DEFAULT 'open',
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS routes (
  id TEXT PRIMARY KEY,
  route TEXT NOT NULL,
  status TEXT NOT NULL,
  risk TEXT,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_stores (
  id TEXT PRIMARY KEY,
  classification TEXT NOT NULL,
  path TEXT,
  notes TEXT,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS planned_items (
  id TEXT PRIMARY KEY,
  classification TEXT NOT NULL,
  status TEXT NOT NULL,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  artifact_type TEXT NOT NULL,
  path TEXT NOT NULL,
  summary TEXT,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS season_summaries (
  season TEXT PRIMARY KEY,
  formula_version TEXT,
  started_at TEXT,
  ended_at TEXT,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proposals (
  proposal_id TEXT PRIMARY KEY,
  xp_season TEXT NOT NULL,
  formula_version TEXT NOT NULL,
  source_agent TEXT NOT NULL,
  proposal_type TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  reasoning TEXT NOT NULL,
  estimated_active_minutes REAL DEFAULT 0,
  requested_xp_wager REAL DEFAULT 0,
  confidence REAL DEFAULT 0,
  risk_level TEXT NOT NULL,
  affected_areas_json TEXT DEFAULT '[]',
  acceptance_criteria_json TEXT DEFAULT '[]',
  rollback_plan TEXT,
  status TEXT NOT NULL,
  decision TEXT,
  decision_note TEXT,
  decision_note_provided INTEGER DEFAULT 0,
  decided_at TEXT,
  simulated_xp_gain REAL DEFAULT 0,
  simulated_xp_loss REAL DEFAULT 0,
  dialogue_messages_json TEXT DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  raw_json TEXT NOT NULL
);
