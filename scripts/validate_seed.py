from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
BOOTSTRAP = ROOT / "archive" / "artifacts" / "bootstrap"
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    ".vite",
    "__pycache__",
    ".pytest_cache",
    "data",
    "logs",
    "runtime",
}

required = [
    CONFIG / "agent-roster.seed.json",
    CONFIG / "expeditions.seed.json",
    CONFIG / "events.seed.json",
    CONFIG / "milestones.seed.json",
    BOOTSTRAP / "agent-census-2026-05-27.redacted.json",
]

schema_seed_map = {
    CONFIG / "agent-roster.seed.json": ("agent", "array"),
    CONFIG / "events.seed.json": ("event", "array"),
    CONFIG / "rooms.seed.json": ("room", "array"),
    CONFIG / "route-edges.seed.json": ("route_edge", "array"),
    CONFIG / "season-policy.seed.json": ("season_policy", "object"),
    CONFIG / "season-summaries.seed.json": ("season_summary", "array"),
    CONFIG / "proposals.seed.json": ("proposal", "array"),
}

def main() -> None:
    for path in sorted(iter_json_files()):
        json.loads(path.read_text(encoding="utf-8"))
        print(f"OK {path.relative_to(ROOT)}")

    for path in required:
        if not path.exists():
            raise SystemExit(f"Missing required file: {path}")

    validate_schema_backed_seeds()

    agents = json.loads((CONFIG / "agent-roster.seed.json").read_text(encoding="utf-8"))
    ids = {a["id"] for a in agents}
    for needed in ["openclaw-main", "codex-memory-operator", "home-windows-codex"]:
        if needed not in ids:
            raise SystemExit(f"Missing expected agent: {needed}")

    rooms_path = CONFIG / "rooms.seed.json"
    route_edges_path = CONFIG / "route-edges.seed.json"
    if rooms_path.exists():
        rooms = json.loads(rooms_path.read_text(encoding="utf-8"))
        room_ids = {room["id"] for room in rooms}
        for agent in agents:
            room = agent.get("room")
            if room and room not in room_ids:
                raise SystemExit(f"Agent {agent['id']} references missing room: {room}")

        if route_edges_path.exists():
            route_edges = json.loads(route_edges_path.read_text(encoding="utf-8"))
            for edge in route_edges:
                for key in ["from_node_id", "to_node_id"]:
                    if edge[key] not in room_ids:
                        raise SystemExit(f"Route edge {edge['id']} references missing room: {edge[key]}")

    expeditions = json.loads((CONFIG / "expeditions.seed.json").read_text(encoding="utf-8"))
    expedition_ids = {expedition["id"] for expedition in expeditions}
    for expedition in expeditions:
        for agent_id in expedition.get("assigned_specialists", []):
            if agent_id not in ids:
                raise SystemExit(f"Expedition {expedition['id']} references missing agent: {agent_id}")

    events_path = CONFIG / "events.seed.json"
    if events_path.exists():
        events = json.loads(events_path.read_text(encoding="utf-8"))
        for event in events:
            source_id = event.get("source_id")
            if source_id and source_id not in ids:
                raise SystemExit(f"Event {event['id']} references missing source agent: {source_id}")
            expedition_id = event.get("expedition_id")
            if expedition_id and expedition_id not in expedition_ids:
                raise SystemExit(f"Event {event['id']} references missing expedition: {expedition_id}")
            for agent_id in event.get("party_agents", []):
                if agent_id not in ids:
                    raise SystemExit(f"Event {event['id']} references missing party agent: {agent_id}")

    field_reports_dir = ROOT / "archive" / "field-reports"
    if field_reports_dir.exists():
        for report_path in sorted(field_reports_dir.glob("*.json")):
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report_label = str(report_path.relative_to(ROOT))
            source_id = report.get("source_id")
            if source_id and source_id != "manual" and source_id not in ids:
                raise SystemExit(f"Field report {report_label} references missing source agent: {source_id}")
            expedition_id = report.get("expedition_id")
            if expedition_id and expedition_id not in expedition_ids:
                raise SystemExit(f"Field report {report_label} references missing expedition: {expedition_id}")
            for agent_id in report.get("party_agents", []):
                if agent_id not in ids:
                    raise SystemExit(f"Field report {report_label} references missing party agent: {agent_id}")
            for artifact_ref in report.get("artifact_refs", []):
                require_repo_local_file(artifact_ref, f"Field report {report_label}")

    proposals_path = CONFIG / "proposals.seed.json"
    if proposals_path.exists():
        proposals = json.loads(proposals_path.read_text(encoding="utf-8"))
        for proposal in proposals:
            source_agent = proposal.get("source_agent")
            if source_agent and source_agent not in ids:
                raise SystemExit(f"Proposal {proposal['proposal_id']} references missing source agent: {source_agent}")
            for vote in proposal.get("council_votes", []):
                agent_id = vote.get("agent_id")
                if agent_id not in ids:
                    raise SystemExit(f"Proposal vote {vote.get('vote_id')} references missing agent: {agent_id}")
                if vote.get("vote") not in {"support", "oppose", "abstain"}:
                    raise SystemExit(f"Proposal vote {vote.get('vote_id')} has invalid vote: {vote.get('vote')}")
                for field in ["reasoning", "expected_benefit", "expected_failure_mode", "risk_notes"]:
                    if not str(vote.get(field) or "").strip():
                        raise SystemExit(f"Proposal vote {vote.get('vote_id')} is missing {field}")

    season_policy_path = CONFIG / "season-policy.seed.json"
    if season_policy_path.exists():
        season_policy = json.loads(season_policy_path.read_text(encoding="utf-8"))
        if season_policy.get("daily_reset_time") != "06:00":
            raise SystemExit("Season policy must keep daily_reset_time at 06:00 for Season 0.x.")
        if season_policy.get("reset_mode") != "display_current_season_only":
            raise SystemExit("Season policy reset_mode must preserve the historical ledger.")
        if season_policy.get("scheduler_source_of_truth") != "windows_task_scheduler":
            raise SystemExit("Season policy must keep Windows Task Scheduler as reset source of truth.")
        if season_policy.get("codex_automation_role") != "audit_report_only":
            raise SystemExit("Season policy must keep Codex automation audit/report only.")
        if season_policy.get("affected_domains") != ["xp_current_season_display", "xp_season_state"]:
            raise SystemExit("Season policy may only affect XP display/state during Season 0.x.")
        preserved = set(season_policy.get("preserve") or [])
        required_preserved = {
            "achievements",
            "milestones",
            "badges",
            "expeditions",
            "events",
            "field_reports",
            "proposal_records",
            "proposal_decision_events",
            "season_summaries",
            "artifacts",
            "routes",
            "rooms",
            "agent_roster",
        }
        missing_preserved = sorted(required_preserved - preserved)
        if missing_preserved:
            raise SystemExit(f"Season policy must preserve non-XP records: {', '.join(missing_preserved)}")
        for key in ["first_season", "initial_restart_at", "timezone"]:
            if not str(season_policy.get(key) or "").strip():
                raise SystemExit(f"Season policy is missing {key}")
    print("Seed validation complete.")

def iter_json_files():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in files:
            if name.endswith(".json"):
                yield Path(root) / name

def require_repo_local_file(ref: str, owner: str) -> None:
    if not str(ref or "").strip():
        raise SystemExit(f"{owner} has an empty artifact ref.")
    candidate = (ROOT / ref).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{owner} artifact ref escapes the repo: {ref}") from exc
    if not candidate.is_file():
        raise SystemExit(f"{owner} artifact ref is missing: {ref}")

def validate_schema_backed_seeds() -> None:
    schema_path = ROOT / "packages" / "schemas" / "expedition-hq.schema.json"
    if not schema_path.exists():
        raise SystemExit(f"Missing schema file: {schema_path}")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_defs = schema.get("properties") or {}
    for seed_path, (schema_key, expected_shape) in schema_seed_map.items():
        if not seed_path.exists():
            continue
        item_schema = schema_defs.get(schema_key)
        if not item_schema:
            raise SystemExit(f"Schema is missing definition: {schema_key}")
        payload = json.loads(seed_path.read_text(encoding="utf-8"))
        if expected_shape == "object":
            validate_schema_record(payload, item_schema, str(seed_path.relative_to(ROOT)))
            continue
        if not isinstance(payload, list):
            raise SystemExit(f"{seed_path.relative_to(ROOT)} must contain a list for schema {schema_key}")
        for index, record in enumerate(payload):
            validate_schema_record(record, item_schema, f"{seed_path.relative_to(ROOT)}[{index}]")

def validate_schema_record(record: dict, schema: dict, label: str) -> None:
    if not isinstance(record, dict):
        raise SystemExit(f"{label} must be an object.")
    for field in schema.get("required", []):
        if field not in record:
            raise SystemExit(f"{label} is missing required schema field: {field}")
    properties = schema.get("properties") or {}
    for field, value in record.items():
        field_schema = properties.get(field)
        if not field_schema:
            continue
        validate_schema_value(value, field_schema, f"{label}.{field}")

def validate_schema_value(value, field_schema: dict, label: str) -> None:
    expected_type = field_schema.get("type")
    if expected_type and not matches_schema_type(value, expected_type):
        raise SystemExit(f"{label} has invalid type: expected {expected_type}, got {type(value).__name__}")
    if "enum" in field_schema and value not in field_schema["enum"]:
        raise SystemExit(f"{label} has invalid value: {value}")
    if isinstance(value, (int, float)):
        if "minimum" in field_schema and value < field_schema["minimum"]:
            raise SystemExit(f"{label} is below minimum {field_schema['minimum']}: {value}")
        if "maximum" in field_schema and value > field_schema["maximum"]:
            raise SystemExit(f"{label} is above maximum {field_schema['maximum']}: {value}")

def matches_schema_type(value, expected_type) -> bool:
    expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
    for kind in expected_types:
        if kind == "null" and value is None:
            return True
        if kind == "string" and isinstance(value, str):
            return True
        if kind == "boolean" and isinstance(value, bool):
            return True
        if kind == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if kind == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if kind == "array" and isinstance(value, list):
            return True
        if kind == "object" and isinstance(value, dict):
            return True
    return False

if __name__ == "__main__":
    main()
