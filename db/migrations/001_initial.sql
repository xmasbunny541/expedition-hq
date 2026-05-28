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
  xp INTEGER DEFAULT 0,
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
