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
from expedition_hq_api.xp import normalize_event_xp

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
        "/season-summaries": 1,
        "/proposals": 5,
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
        "active_minutes": 30,
        "party_agents": ["openclaw-main"],
        "scoring_multipliers": {
            "artifact": 1.15,
            "blocker_break": 1.0,
            "reuse_leverage": 1.0,
            "risk_control": 1.25,
        },
        "evidence_refs": ["apps/api/tests/test_seed_files.py::test_post_events_creates_local_event"],
        "tags": ["test"],
    }

    response = seeded_client.post("/events", json=payload)
    assert response.status_code == 200
    created = response.json()
    assert created["id"] == payload["id"]
    assert created["timestamp"]
    assert created["base_xp"] == 0.5
    assert created["scoring_multipliers"]["grinding"] == 1.25
    assert created["scoring_multipliers"]["party_size"] == 1.1
    assert created["total_multiplier_raw"] == 1.976562
    assert created["awarded_xp"] == 0.988281
    assert created["xp"] == created["awarded_xp"]
    assert created["evidence_refs"] == payload["evidence_refs"]
    assert created["xp_claim_status"] == "review_pending"
    assert created["review_flags"] == ["unknown_source"]

    events = seeded_client.get("/events").json()
    assert any(event["id"] == payload["id"] for event in events)


def test_xp_claim_endpoint_accepts_cross_project_claim_with_evidence(seeded_client):
    payload = {
        "id": "evt-test-cross-project-claim",
        "source_id": "openclaw-main",
        "source_project": "C:/Users/augus/Desktop/outside-work",
        "expedition_id": "outside-work-calibration",
        "event_type": "cross_project_work",
        "title": "Cross-project XP claim",
        "summary": "Records useful outside-project work with reviewable evidence for Season 0.x calibration.",
        "active_minutes": 15,
        "evidence_refs": ["C:/Users/augus/Desktop/outside-work/logs/claim.txt"],
        "tags": ["cross-project", "calibration"],
    }

    response = seeded_client.post("/xp-claims", json=payload)
    assert response.status_code == 200
    created = response.json()

    assert created["source_project"] == payload["source_project"]
    assert created["xp_claim_status"] == "calibration_awarded"
    assert created["review_flags"] == []
    assert created["awarded_xp"] > 0


def test_xp_claim_endpoint_flags_missing_evidence_without_rejecting(seeded_client):
    payload = {
        "id": "evt-test-missing-evidence-claim",
        "source_id": "openclaw-main",
        "expedition_id": "expedition-hq-dashboard",
        "event_type": "stress_probe",
        "title": "Missing evidence probe",
        "summary": "Deliberately submits a nonzero Season 0.x claim without evidence so the ledger flags it.",
        "active_minutes": 12,
    }

    response = seeded_client.post("/xp-claims", json=payload)
    assert response.status_code == 200
    created = response.json()

    assert created["awarded_xp"] > 0
    assert created["needs_review"] is True
    assert created["xp_claim_status"] == "review_pending"
    assert created["review_flags"] == ["missing_evidence"]


def test_post_events_rejects_agent_supplied_awarded_xp(seeded_client):
    payload = {
        "id": "evt-test-self-award",
        "source_id": "openclaw-main",
        "expedition_id": "expedition-hq-dashboard",
        "event_type": "self_award_probe",
        "title": "Self award probe",
        "summary": "Attempts to set final awarded XP directly, which the API must reject.",
        "active_minutes": 1,
        "awarded_xp": 999,
    }

    response = seeded_client.post("/events", json=payload)
    assert response.status_code == 422


def test_agents_include_visible_xp_status(seeded_client):
    response = seeded_client.get("/agents")
    assert response.status_code == 200
    agents = response.json()
    openclaw = next(agent for agent in agents if agent["id"] == "openclaw-main")

    assert openclaw["xp_status"]["awarded_xp"] > 0
    assert openclaw["xp_status"]["event_count"] > 0
    assert "claim_status_counts" in openclaw["xp_status"]


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

def proposal_payload(proposal_id: str, status: str = "pending") -> dict:
    return {
        "proposal_id": proposal_id,
        "source_agent": "test-harness",
        "proposal_type": "discovery",
        "title": f"Proposal {proposal_id}",
        "summary": "Local proposal API test record.",
        "reasoning": "Verifies soft wager proposal handling without external mutation.",
        "estimated_active_minutes": 45,
        "requested_xp_wager": 1.75,
        "confidence": 0.64,
        "risk_level": "low",
        "affected_areas": ["proposal_desk"],
        "acceptance_criteria": ["The proposal can be reviewed locally."],
        "rollback_plan": "Delete the local proposal test record.",
        "status": status,
    }

def test_get_proposal_by_id_and_unknown_404(seeded_client):
    response = seeded_client.get("/proposals/proposal-hq-rooms-inhabited")
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["title"] == "Make HQ rooms more visually inhabited"
    assert proposal["status"] == "pending"

    missing = seeded_client.get("/proposals/proposal-does-not-exist")
    assert missing.status_code == 404

def test_qa_denial_seed_proposal_is_pending_and_marked_test_only(seeded_client):
    response = seeded_client.get("/proposals/proposal-qa-deny-live-controls")
    assert response.status_code == 200
    proposal = response.json()

    assert proposal["title"] == "Add live tunnel/token/OpenClaw control buttons immediately"
    assert proposal["status"] == "pending"
    assert proposal["proposal_type"] == "safety"
    assert proposal["risk_level"] == "high"
    assert proposal["requested_xp_wager"] == 1
    assert proposal["confidence"] == 0.9
    assert proposal["estimated_active_minutes"] == 30
    assert proposal["is_test_proposal"] is True
    assert proposal["expected_decision"] == "deny"
    assert proposal["excluded_from_reputation"] is True
    assert "Would add live control actions" in proposal["acceptance_criteria"]
    assert "Not applicable" in proposal["rollback_plan"]

def test_post_proposals_creates_pending_and_rejects_duplicate_ids(seeded_client):
    payload = proposal_payload("proposal-api-create")
    response = seeded_client.post("/proposals", json=payload)
    assert response.status_code == 200
    created = response.json()

    assert created["proposal_id"] == payload["proposal_id"]
    assert created["status"] == "pending"
    assert created["xp_season"] == "0.1"
    assert created["formula_version"] == "xp_calibration_v0_1"
    assert created["simulated_xp_gain"] == 0
    assert created["simulated_xp_loss"] == 0

    duplicate = seeded_client.post("/proposals", json=payload)
    assert duplicate.status_code == 409

def test_post_proposals_allows_only_draft_or_pending_creation(seeded_client):
    response = seeded_client.post(
        "/proposals",
        json=proposal_payload("proposal-invalid-status", status="approved"),
    )
    assert response.status_code == 422

def test_proposal_decisions_update_status_and_soft_wager_loss(seeded_client):
    expected = {
        "approve": ("approved", 0),
        "deny": ("denied", 1.75),
        "revise": ("revise_requested", 0),
        "defer": ("deferred", 0),
    }

    for decision, (status, simulated_loss) in expected.items():
        proposal_id = f"proposal-decision-{decision}"
        create = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
        assert create.status_code == 200

        response = seeded_client.patch(
            f"/proposals/{proposal_id}/decision",
            json={
                "decision": decision,
                "decision_note": f"{decision} during local API test.",
            },
        )
        assert response.status_code == 200
        proposal = response.json()
        assert proposal["status"] == status
        assert proposal["decision"] == decision
        assert proposal["decision_note"] == f"{decision} during local API test."
        assert proposal["simulated_xp_loss"] == simulated_loss
        assert proposal["simulated_xp_gain"] == 0

def test_proposal_decisions_accept_missing_notes_and_store_defaults(seeded_client):
    expected = {
        "approve": ("approved", "Approved for planning. No implementation triggered."),
        "deny": ("denied", "Denied during Season 0.x testing. No implementation triggered."),
        "revise": ("revise_requested", "Revision requested during Season 0.x testing. Agent should ask follow-up questions before resubmitting."),
        "defer": ("deferred", "Deferred during Season 0.x testing. No implementation triggered."),
    }

    for decision, (status, default_note) in expected.items():
        proposal_id = f"proposal-default-note-{decision}"
        create = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
        assert create.status_code == 200

        response = seeded_client.patch(
            f"/proposals/{proposal_id}/decision",
            json={"decision": decision},
        )
        assert response.status_code == 200
        proposal = response.json()
        assert proposal["status"] == status
        assert proposal["decision"] == decision
        assert proposal["decision_note"] == default_note
        assert proposal["decision_note_provided"] is False
        assert proposal["simulated_xp_gain"] == 0
        if decision == "deny":
            assert proposal["simulated_xp_loss"] == proposal["requested_xp_wager"]
        else:
            assert proposal["simulated_xp_loss"] == 0

def test_proposal_decision_creates_zero_xp_local_event(seeded_client):
    proposal_id = "proposal-decision-event"
    created = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
    assert created.status_code == 200

    response = seeded_client.patch(
        f"/proposals/{proposal_id}/decision",
        json={
            "decision": "deny",
            "decision_note": "Denied to verify local event ledger recording.",
        },
    )
    assert response.status_code == 200

    events = seeded_client.get("/events").json()
    decision_events = [
        event for event in events
        if event["event_type"] == "proposal_decision" and event.get("proposal_id") == proposal_id
    ]
    assert len(decision_events) == 1
    event = decision_events[0]
    assert event["source_id"] == "expedition-hq-dashboard"
    assert event["expedition_id"] == "expedition-hq-dashboard"
    assert event["active_minutes"] == 0
    assert event["base_xp"] == 0
    assert event["awarded_xp"] == 0
    assert event["total_multiplier_raw"] == 1
    assert event["tags"] == ["proposal", "soft-wager", "deny"]

def test_revise_creates_revision_event_and_clarification_questions(seeded_client):
    proposal_id = "proposal-revise-dialogue"
    created = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
    assert created.status_code == 200

    response = seeded_client.patch(
        f"/proposals/{proposal_id}/decision",
        json={"decision": "revise", "decision_note": ""},
    )
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["status"] == "revise_requested"
    assert proposal["decision"] == "revise"
    assert proposal["simulated_xp_loss"] == 0
    assert proposal["decision_note"] == "Revision requested during Season 0.x testing. Agent should ask follow-up questions before resubmitting."

    messages = proposal["dialogue_messages"]
    assert any(message["message_type"] == "decision_note" for message in messages)
    questions = [
        message["message"] for message in messages
        if message["message_type"] == "clarification_question"
    ]
    assert "What did you not like about this proposal?" in questions
    assert "What would make this proposal acceptable?" in questions

    events = seeded_client.get("/events").json()
    revision_events = [
        event for event in events
        if event["event_type"] == "proposal_revision_requested" and event.get("proposal_id") == proposal_id
    ]
    assert len(revision_events) == 1
    event = revision_events[0]
    assert event["active_minutes"] == 0
    assert event["awarded_xp"] == 0
    assert event["decision_note"] == proposal["decision_note"]
    assert proposal["decision_note"] in event["summary"]
    assert event["tags"] == ["proposal", "soft-wager", "revise", "clarification"]

def test_qa_denial_seed_proposal_deny_path(seeded_client):
    proposal_id = "proposal-qa-deny-live-controls"
    decision_note = (
        "Denied because this violates the read-only Observatory posture. Expedition HQ must not add live tunnel "
        "controls, token rotation, OpenClaw config mutation, memory mutation, external sends, or production MCP "
        "controls during the MVP/calibration phase."
    )

    response = seeded_client.patch(
        f"/proposals/{proposal_id}/decision",
        json={
            "decision": "deny",
            "decision_note": decision_note,
        },
    )
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["status"] == "denied"
    assert proposal["decision"] == "deny"
    assert proposal["decision_note"] == decision_note
    assert proposal["decided_at"]
    assert proposal["simulated_xp_loss"] == proposal["requested_xp_wager"] == 1
    assert proposal["simulated_xp_gain"] == 0
    assert proposal["is_test_proposal"] is True
    assert proposal["excluded_from_reputation"] is True

    events = seeded_client.get("/events").json()
    decision_events = [
        event for event in events
        if event["event_type"] == "proposal_decision" and event.get("proposal_id") == proposal_id
    ]
    assert len(decision_events) == 1
    event = decision_events[0]
    assert event["active_minutes"] == 0
    assert event["awarded_xp"] == 0
    assert event["tags"] == ["proposal", "soft-wager", "deny"]
    assert "requested soft wager 1 XP" in event["summary"]

def test_proposal_decision_backend_has_no_external_dispatch_terms():
    checked_files = [
        ROOT / "apps" / "api" / "expedition_hq_api" / "main.py",
        ROOT / "apps" / "api" / "expedition_hq_api" / "db.py",
        ROOT / "apps" / "api" / "expedition_hq_api" / "proposals.py",
    ]
    forbidden = [
        "hooks/agent",
        "codex exec",
        "OpenClaw",
        "Start-Process",
        "subprocess",
        "shell",
        "dispatch",
        "tunnel",
        "token",
        "memory mutation",
        "Invoke-RestMethod",
        "curl",
        "requests.",
        "httpx.",
    ]
    contents = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)
    assert not any(term in contents for term in forbidden)

def test_proposal_decision_does_not_apply_real_xp_to_season_summary(seeded_client):
    proposal_id = "proposal-no-real-xp"
    created = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
    assert created.status_code == 200

    before = seeded_client.get("/season-summaries").json()[0]
    response = seeded_client.patch(
        f"/proposals/{proposal_id}/decision",
        json={
            "decision": "deny",
            "decision_note": "Denied to verify soft wagers stay separate from real XP.",
        },
    )
    assert response.status_code == 200
    after = seeded_client.get("/season-summaries").json()[0]

    assert after["total_active_minutes"] == before["total_active_minutes"]
    assert after["total_base_xp"] == before["total_base_xp"]
    assert after["total_awarded_xp"] == before["total_awarded_xp"]

def test_xp_formula_party_cap_and_uncapped_total():
    event = normalize_event_xp({
        "id": "evt-xp-formula",
        "timestamp": "2026-05-28T10:00:00-07:00",
        "source_id": "openclaw-main",
        "event_type": "calibration_probe",
        "title": "Formula probe",
        "summary": "Checks Season 0.x XP formulas.",
        "status": "success",
        "risk_level": "low",
        "needs_review": False,
        "active_minutes": 120,
        "party_agents": ["a", "b", "c", "d", "e", "f"],
        "scoring_multipliers": {
            "artifact": 1.3,
            "blocker_break": 1.5,
            "reuse_leverage": 2.0,
            "risk_control": 1.25,
        },
        "shadow_multipliers": {
            "discovery": True,
            "polish": True,
        },
    })

    assert event["base_xp"] == 2
    assert event["scoring_multipliers"]["grinding"] == 1.5
    assert event["scoring_multipliers"]["party_size"] == 1.5
    assert event["total_multiplier_raw"] == 10.96875
    assert event["awarded_xp"] == 21.9375
    assert event["multiplier_cap"] is None
    assert event["scaling_flags"] == ["high_multiplier", "extreme_multiplier", "scaling_review"]

def test_shadow_multipliers_do_not_change_xp():
    base_payload = {
        "id": "evt-shadow-base",
        "timestamp": "2026-05-28T10:00:00-07:00",
        "source_id": "openclaw-main",
        "event_type": "calibration_probe",
        "title": "Formula probe",
        "summary": "Checks shadow tags.",
        "status": "success",
        "risk_level": "low",
        "needs_review": False,
        "active_minutes": 45,
        "scoring_multipliers": {
            "artifact": 1.15,
            "blocker_break": 1.0,
            "reuse_leverage": 1.3,
            "risk_control": 1.0,
        },
    }
    without_shadow = normalize_event_xp(base_payload)
    with_shadow = normalize_event_xp({
        **base_payload,
        "id": "evt-shadow-candidate",
        "shadow_multipliers": {
            "discovery": True,
            "handoff_chain": True,
            "polish": True,
            "sentimental_record": True,
        },
    })

    assert with_shadow["awarded_xp"] == without_shadow["awarded_xp"]
    assert with_shadow["total_multiplier_raw"] == without_shadow["total_multiplier_raw"]

def test_season_summary_aggregates_seed_xp(seeded_client):
    summaries = seeded_client.get("/season-summaries")
    assert summaries.status_code == 200
    season = summaries.json()[0]

    assert season["season"] == "0.1"
    assert season["formula_version"] == "xp_calibration_v0_1"
    assert season["event_count"] >= 9
    assert season["total_active_minutes"] >= 368
    assert season["total_base_xp"] >= 6.133333
    assert season["average_multiplier"] > 1
    assert season["shadow_multiplier_counts"]["discovery"] >= 3
