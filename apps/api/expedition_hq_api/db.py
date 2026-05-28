from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

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
]
READ_TABLES = set(SEED_TABLES)

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

def insert_event(conn: sqlite3.Connection, event: dict[str, Any]) -> None:
    conn.execute(
        '''
        INSERT INTO events
        (id, timestamp, source_id, expedition_id, event_type, title, summary, status,
         risk_level, needs_review, xp, tags_json, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            event["id"], event["timestamp"], event["source_id"], event.get("expedition_id"),
            event["event_type"], event["title"], event["summary"], event["status"],
            event.get("risk_level"), 1 if event.get("needs_review") else 0,
            event.get("xp", 0), json.dumps(event.get("tags", [])), json.dumps(event)
        )
    )

def insert_seed_event(conn: sqlite3.Connection, event: dict[str, Any]) -> None:
    conn.execute(
        '''
        INSERT OR IGNORE INTO events
        (id, timestamp, source_id, expedition_id, event_type, title, summary, status,
         risk_level, needs_review, xp, tags_json, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            event["id"], event["timestamp"], event["source_id"], event.get("expedition_id"),
            event["event_type"], event["title"], event["summary"], event["status"],
            event.get("risk_level"), 1 if event.get("needs_review") else 0,
            event.get("xp", 0), json.dumps(event.get("tags", [])), json.dumps(event)
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
        "xp": report.get("xp", 0),
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
