from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from .proposals import apply_decision, normalize_proposal, proposal_decision_event
from .xp import aggregate_season_summary, normalize_event_xp

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = ROOT / "data" / "expedition-hq.db"
MIGRATION_PATH = ROOT / "db" / "migrations" / "001_initial.sql"
SEED_TABLES = [
    "agents",
    "expeditions",
    "events",
    "milestones",
    "incidents",
    "routes",
    "memory_stores",
    "planned_items",
    "artifacts",
    "season_summaries",
    "proposals",
]
READ_TABLES = set(SEED_TABLES)
EVENT_COMPAT_COLUMNS = {
    "xp_season": "TEXT",
    "formula_version": "TEXT",
    "xp_mode": "TEXT",
    "active_minutes": "REAL DEFAULT 0",
    "base_xp": "REAL DEFAULT 0",
    "awarded_xp": "REAL DEFAULT 0",
    "total_multiplier_raw": "REAL DEFAULT 1",
    "multiplier_cap": "REAL",
    "xp_source": "TEXT",
    "xp_confidence": "TEXT",
    "party_agents_json": "TEXT DEFAULT '[]'",
    "party_size": "INTEGER DEFAULT 0",
    "scoring_multipliers_json": "TEXT DEFAULT '{}'",
    "shadow_multipliers_json": "TEXT DEFAULT '{}'",
    "shadow_multiplier_notes_json": "TEXT DEFAULT '[]'",
    "multiplier_notes_json": "TEXT DEFAULT '[]'",
    "scaling_flags_json": "TEXT DEFAULT '[]'",
}
PROPOSAL_COMPAT_COLUMNS = {
    "decision_note_provided": "INTEGER DEFAULT 0",
    "dialogue_messages_json": "TEXT DEFAULT '[]'",
}

def db_path() -> Path:
    return Path(os.environ.get("EXPEDITION_HQ_DB_PATH", DEFAULT_DB_PATH))

def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with connect() as conn:
        conn.executescript(MIGRATION_PATH.read_text(encoding="utf-8"))
        ensure_compatible_schema(conn)

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def seed_db(force: bool = False) -> None:
    init_db()
    seed_dir = ROOT / "config"
    with connect() as conn:
        if force:
            for table in SEED_TABLES:
                conn.execute(f"DELETE FROM {table}")

        agents = load_json(seed_dir / "agent-roster.seed.json")
        for a in agents:
            conn.execute(
                '''
                INSERT OR REPLACE INTO agents
                (id, display_name, visual_name, source_classification, visual_class, status, ui_state,
                 visual_archetype, room, current_assignment, summary, decision_mode, needs_august_review,
                 logs_history, allowed_as_little_guy, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    a["id"], a["display_name"], a.get("visual_name"), a.get("source_classification"),
                    a["visual_class"], a["status"], a["ui_state"], a.get("visual_archetype"),
                    a.get("room"), a.get("current_assignment"), a.get("summary"), a.get("decision_mode"),
                    a.get("needs_august_review"), json.dumps(a.get("logs_history")),
                    1 if a.get("allowed_as_little_guy") else 0, json.dumps(a)
                )
            )

        expeditions = load_json(seed_dir / "expeditions.seed.json")
        for e in expeditions:
            conn.execute(
                '''
                INSERT OR REPLACE INTO expeditions
                (id, name, status, summary, campaign, priority, progress_percent, next_objective, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    e["id"], e["name"], e["status"], e.get("summary"), e.get("campaign"),
                    e.get("priority"), e.get("progress_percent", 0), e.get("next_objective"),
                    json.dumps(e)
                )
            )

        events = load_json(seed_dir / "events.seed.json")
        for event in events:
            insert_seed_event(conn, event)

        field_reports_dir = ROOT / "archive" / "field-reports"
        if field_reports_dir.exists():
            for report_path in sorted(field_reports_dir.glob("*.json")):
                report = load_json(report_path)
                insert_seed_event(conn, field_report_to_event(report, report_path))

        milestones = load_json(seed_dir / "milestones.seed.json")
        for m in milestones:
            conn.execute(
                '''
                INSERT OR REPLACE INTO milestones
                (id, name, description, status, xp_reward, unlock_condition, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    m["id"], m["name"], m.get("description"), m.get("status"),
                    m.get("xp_reward", 0), m.get("unlock_condition"), json.dumps(m)
                )
            )

        blockers_path = seed_dir / "blockers.seed.json"
        if blockers_path.exists():
            for b in load_json(blockers_path):
                incident = {**b, "status": b.get("status", "open")}
                conn.execute(
                    '''
                    INSERT OR REPLACE INTO incidents
                    (id, summary, impact, status, raw_json)
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (
                        incident["id"], incident["summary"], incident.get("impact"),
                        incident["status"], json.dumps(incident)
                    )
                )

        routes_path = seed_dir / "routes.seed.json"
        if routes_path.exists():
            for route in load_json(routes_path):
                conn.execute(
                    '''
                    INSERT OR REPLACE INTO routes
                    (id, route, status, risk, raw_json)
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (
                        route["id"], route["route"], route["status"],
                        route.get("risk"), json.dumps(route)
                    )
                )

        memory_stores_path = seed_dir / "memory-stores.seed.json"
        if memory_stores_path.exists():
            for store in load_json(memory_stores_path):
                conn.execute(
                    '''
                    INSERT OR REPLACE INTO memory_stores
                    (id, classification, path, notes, raw_json)
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (
                        store["id"], store["classification"], store.get("path"),
                        store.get("notes"), json.dumps(store)
                    )
                )

        planned_path = seed_dir / "planned.seed.json"
        if planned_path.exists():
            for item in load_json(planned_path):
                conn.execute(
                    '''
                    INSERT OR REPLACE INTO planned_items
                    (id, classification, status, raw_json)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (
                        item["id"], item["classification"], item["status"],
                        json.dumps(item)
                    )
                )

        insert_bootstrap_artifacts(conn)

        season_summaries_path = seed_dir / "season-summaries.seed.json"
        if season_summaries_path.exists():
            for summary in load_json(season_summaries_path):
                insert_season_summary(conn, summary)

        proposals_path = seed_dir / "proposals.seed.json"
        if proposals_path.exists():
            for proposal in load_json(proposals_path):
                insert_seed_proposal(conn, proposal)

def insert_event(conn: sqlite3.Connection, event: dict[str, Any]) -> None:
    event = normalize_event_xp(event)
    conn.execute(
        '''
        INSERT INTO events
        (id, timestamp, source_id, expedition_id, event_type, title, summary, status,
         risk_level, needs_review, xp, xp_season, formula_version, xp_mode, active_minutes,
         base_xp, awarded_xp, total_multiplier_raw, multiplier_cap, xp_source, xp_confidence,
         party_agents_json, party_size, scoring_multipliers_json, shadow_multipliers_json,
         shadow_multiplier_notes_json, multiplier_notes_json, scaling_flags_json, tags_json, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            event["id"], event["timestamp"], event["source_id"], event.get("expedition_id"),
            event["event_type"], event["title"], event["summary"], event["status"],
            event.get("risk_level"), 1 if event.get("needs_review") else 0,
            event.get("xp", 0), event.get("xp_season"), event.get("formula_version"),
            event.get("xp_mode"), event.get("active_minutes"), event.get("base_xp"),
            event.get("awarded_xp"), event.get("total_multiplier_raw"), event.get("multiplier_cap"),
            event.get("xp_source"), event.get("xp_confidence"), json.dumps(event.get("party_agents", [])),
            event.get("party_size", 0), json.dumps(event.get("scoring_multipliers", {})),
            json.dumps(event.get("shadow_multipliers", {})), json.dumps(event.get("shadow_multiplier_notes", [])),
            json.dumps(event.get("multiplier_notes", [])), json.dumps(event.get("scaling_flags", [])),
            json.dumps(event.get("tags", [])), json.dumps(event)
        )
    )

def insert_seed_event(conn: sqlite3.Connection, event: dict[str, Any]) -> None:
    event = normalize_event_xp(event)
    conn.execute(
        '''
        INSERT OR REPLACE INTO events
        (id, timestamp, source_id, expedition_id, event_type, title, summary, status,
         risk_level, needs_review, xp, xp_season, formula_version, xp_mode, active_minutes,
         base_xp, awarded_xp, total_multiplier_raw, multiplier_cap, xp_source, xp_confidence,
         party_agents_json, party_size, scoring_multipliers_json, shadow_multipliers_json,
         shadow_multiplier_notes_json, multiplier_notes_json, scaling_flags_json, tags_json, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            event["id"], event["timestamp"], event["source_id"], event.get("expedition_id"),
            event["event_type"], event["title"], event["summary"], event["status"],
            event.get("risk_level"), 1 if event.get("needs_review") else 0,
            event.get("xp", 0), event.get("xp_season"), event.get("formula_version"),
            event.get("xp_mode"), event.get("active_minutes"), event.get("base_xp"),
            event.get("awarded_xp"), event.get("total_multiplier_raw"), event.get("multiplier_cap"),
            event.get("xp_source"), event.get("xp_confidence"), json.dumps(event.get("party_agents", [])),
            event.get("party_size", 0), json.dumps(event.get("scoring_multipliers", {})),
            json.dumps(event.get("shadow_multipliers", {})), json.dumps(event.get("shadow_multiplier_notes", [])),
            json.dumps(event.get("multiplier_notes", [])), json.dumps(event.get("scaling_flags", [])),
            json.dumps(event.get("tags", [])), json.dumps(event)
        )
    )

def field_report_to_event(report: dict[str, Any], report_path: Path) -> dict[str, Any]:
    return {
        "id": report["id"],
        "timestamp": report["timestamp"],
        "source_id": report.get("source_id", "manual"),
        "expedition_id": report.get("expedition_id"),
        "event_type": "field_report",
        "title": report["title"],
        "summary": report["summary"],
        "status": "success",
        "risk_level": "low",
        "needs_review": False,
        "active_minutes": report.get("active_minutes", 0),
        "xp_confidence": report.get("xp_confidence", "estimated"),
        "party_agents": report.get("party_agents", []),
        "scoring_multipliers": report.get("scoring_multipliers", {}),
        "shadow_multipliers": report.get("shadow_multipliers", {}),
        "shadow_multiplier_notes": report.get("shadow_multiplier_notes", []),
        "multiplier_notes": report.get("multiplier_notes", []),
        "tags": ["field-report", "bootstrap"],
        "artifact_refs": report.get("artifact_refs", []),
        "field_report_path": str(report_path.relative_to(ROOT)).replace("\\", "/"),
    }

def insert_bootstrap_artifacts(conn: sqlite3.Connection) -> None:
    artifacts = [
        {
            "id": "artifact-bootstrap-agent-census-2026-05-27",
            "title": "Redacted Agent Census",
            "artifact_type": "redacted_census",
            "path": "archive/artifacts/bootstrap/agent-census-2026-05-27.redacted.json",
            "summary": "Redacted census of agents, routes, tools, memory stores, workflows, and blockers.",
        },
        {
            "id": "artifact-bootstrap-deep-research-report",
            "title": "Bootstrap Research Report",
            "artifact_type": "research_report",
            "path": "archive/artifacts/bootstrap/deep-research-report.md",
            "summary": "Planning report used to shape the first Expedition HQ build.",
        },
    ]
    for artifact in artifacts:
        artifact_path = ROOT / artifact["path"]
        if artifact_path.exists():
            conn.execute(
                '''
                INSERT OR REPLACE INTO artifacts
                (id, title, artifact_type, path, summary, raw_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (
                    artifact["id"], artifact["title"], artifact["artifact_type"],
                    artifact["path"], artifact["summary"], json.dumps(artifact)
                )
            )

def event_exists(conn: sqlite3.Connection, event_id: str) -> bool:
    row = conn.execute("SELECT 1 FROM events WHERE id = ?", (event_id,)).fetchone()
    return row is not None

def rows(table: str) -> list[dict[str, Any]]:
    if table not in READ_TABLES:
        raise ValueError(f"Unsupported table: {table}")
    with connect() as conn:
        out = []
        for row in conn.execute(f"SELECT raw_json FROM {table}"):
            out.append(json.loads(row["raw_json"]))
        return out

def season_summary_rows() -> list[dict[str, Any]]:
    seed_summaries = {summary["season"]: summary for summary in rows("season_summaries")}
    events_by_season: dict[str, list[dict[str, Any]]] = {}
    for event in rows("events"):
        event = normalize_event_xp(event)
        events_by_season.setdefault(event["xp_season"], []).append(event)

    summaries = []
    for season in sorted(set(seed_summaries) | set(events_by_season)):
        summaries.append(aggregate_season_summary(events_by_season.get(season, []), seed_summaries.get(season)))
    return summaries

def insert_season_summary(conn: sqlite3.Connection, summary: dict[str, Any]) -> None:
    conn.execute(
        '''
        INSERT OR REPLACE INTO season_summaries
        (season, formula_version, started_at, ended_at, raw_json)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (
            summary["season"], summary.get("formula_version"),
            summary.get("started_at"), summary.get("ended_at"), json.dumps(summary)
        )
    )

def insert_proposal(conn: sqlite3.Connection, proposal: dict[str, Any]) -> dict[str, Any]:
    proposal = normalize_proposal(proposal)
    conn.execute(
        '''
        INSERT INTO proposals
        (proposal_id, xp_season, formula_version, source_agent, proposal_type, title, summary,
         reasoning, estimated_active_minutes, requested_xp_wager, confidence, risk_level,
         affected_areas_json, acceptance_criteria_json, rollback_plan, status, decision,
         decision_note, decision_note_provided, decided_at, simulated_xp_gain, simulated_xp_loss,
         dialogue_messages_json, created_at, updated_at, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        proposal_values(proposal)
    )
    return proposal

def insert_seed_proposal(conn: sqlite3.Connection, proposal: dict[str, Any]) -> dict[str, Any]:
    proposal = normalize_proposal(proposal)
    conn.execute(
        '''
        INSERT OR IGNORE INTO proposals
        (proposal_id, xp_season, formula_version, source_agent, proposal_type, title, summary,
         reasoning, estimated_active_minutes, requested_xp_wager, confidence, risk_level,
         affected_areas_json, acceptance_criteria_json, rollback_plan, status, decision,
         decision_note, decision_note_provided, decided_at, simulated_xp_gain, simulated_xp_loss,
         dialogue_messages_json, created_at, updated_at, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        proposal_values(proposal)
    )
    return proposal

def proposal_values(proposal: dict[str, Any]) -> tuple[Any, ...]:
    return (
        proposal["proposal_id"], proposal["xp_season"], proposal["formula_version"],
        proposal["source_agent"], proposal["proposal_type"], proposal["title"],
        proposal["summary"], proposal["reasoning"], proposal["estimated_active_minutes"],
        proposal["requested_xp_wager"], proposal["confidence"], proposal["risk_level"],
        json.dumps(proposal["affected_areas"]), json.dumps(proposal["acceptance_criteria"]),
        proposal.get("rollback_plan"), proposal["status"], proposal.get("decision"),
        proposal.get("decision_note"), 1 if proposal.get("decision_note_provided") else 0,
        proposal.get("decided_at"), proposal["simulated_xp_gain"], proposal["simulated_xp_loss"],
        json.dumps(proposal.get("dialogue_messages", [])), proposal["created_at"],
        proposal["updated_at"], json.dumps(proposal)
    )

def proposal_exists(conn: sqlite3.Connection, proposal_id: str) -> bool:
    row = conn.execute("SELECT 1 FROM proposals WHERE proposal_id = ?", (proposal_id,)).fetchone()
    return row is not None

def proposal_by_id(proposal_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT raw_json FROM proposals WHERE proposal_id = ?",
            (proposal_id,)
        ).fetchone()
    return json.loads(row["raw_json"]) if row else None

def update_proposal_decision(
    conn: sqlite3.Connection,
    proposal_id: str,
    decision: str,
    decision_note: str | None,
) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT raw_json FROM proposals WHERE proposal_id = ?",
        (proposal_id,)
    ).fetchone()
    if row is None:
        return None

    proposal = apply_decision(json.loads(row["raw_json"]), decision, decision_note)
    conn.execute(
        '''
        UPDATE proposals
        SET status = ?, decision = ?, decision_note = ?, decided_at = ?,
            decision_note_provided = ?, simulated_xp_gain = ?, simulated_xp_loss = ?,
            dialogue_messages_json = ?, updated_at = ?, raw_json = ?
        WHERE proposal_id = ?
        ''',
        (
            proposal["status"], proposal["decision"], proposal["decision_note"],
            proposal["decided_at"], 1 if proposal.get("decision_note_provided") else 0,
            proposal["simulated_xp_gain"], proposal["simulated_xp_loss"],
            json.dumps(proposal.get("dialogue_messages", [])), proposal["updated_at"],
            json.dumps(proposal), proposal_id
        )
    )
    insert_event(conn, proposal_decision_event(proposal))
    return proposal

def ensure_compatible_schema(conn: sqlite3.Connection) -> None:
    event_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(events)").fetchall()
    }
    for column, definition in EVENT_COMPAT_COLUMNS.items():
        if column not in event_columns:
            conn.execute(f"ALTER TABLE events ADD COLUMN {column} {definition}")
    proposal_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(proposals)").fetchall()
    }
    for column, definition in PROPOSAL_COMPAT_COLUMNS.items():
        if column not in proposal_columns:
            conn.execute(f"ALTER TABLE proposals ADD COLUMN {column} {definition}")
