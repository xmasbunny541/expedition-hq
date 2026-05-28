import importlib
import json
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from expedition_hq_api import db as db_module
from expedition_hq_api.main import app

def test_seed_json_loads():
    for path in (ROOT / "config").glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

def test_agent_seed_has_coordinator():
    agents = json.loads((ROOT / "config" / "agent-roster.seed.json").read_text(encoding="utf-8"))
    assert any(a["id"] == "openclaw-main" for a in agents)

@pytest.fixture()
def seeded_client(tmp_path, monkeypatch):
    monkeypatch.setenv("EXPEDITION_HQ_DB_PATH", str(tmp_path / "expedition-hq-test.db"))
    importlib.reload(db_module)
    db_module.seed_db(force=True)
    with TestClient(app) as client:
        yield client

def test_required_endpoints_return_seeded_data(seeded_client):
    expected_counts = {
        "/agents": 18,
        "/expeditions": 6,
        "/events": 9,
        "/milestones": 5,
        "/incidents": 7,
        "/routes": 6,
        "/memory-stores": 6,
        "/planned": 4,
        "/artifacts": 2,
    }

    health = seeded_client.get("/health")
    assert health.status_code == 200
    assert health.json()["mutation_policy"] == "local_sqlite_events_only"

    for path, minimum in expected_counts.items():
        response = seeded_client.get(path)
        assert response.status_code == 200
        assert len(response.json()) >= minimum

    incidents = seeded_client.get("/incidents").json()
    assert all(incident["status"] == "open" for incident in incidents)

def test_public_seed_endpoint_is_not_available(seeded_client):
    response = seeded_client.post("/seed")
    assert response.status_code == 404

def test_post_events_creates_local_event(seeded_client):
    payload = {
        "id": "evt-test-local-create",
        "source_id": "test-harness",
        "expedition_id": "expedition-hq-dashboard",
        "event_type": "field_report",
        "title": "Test field report",
        "summary": "Verifies local SQLite event ingest without touching external systems.",
        "tags": ["test"],
    }

    response = seeded_client.post("/events", json=payload)
    assert response.status_code == 200
    created = response.json()
    assert created["id"] == payload["id"]
    assert created["timestamp"]

    events = seeded_client.get("/events").json()
    assert any(event["id"] == payload["id"] for event in events)

def test_post_events_rejects_duplicate_ids(seeded_client):
    payload = {
        "id": "evt-bootstrap-001",
        "source_id": "test-harness",
        "event_type": "duplicate_check",
        "title": "Duplicate check",
        "summary": "This should not replace a seeded bootstrap event.",
    }

    response = seeded_client.post("/events", json=payload)
    assert response.status_code == 409
