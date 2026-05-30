import importlib
import json
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "api"))
sys.path.insert(0, str(ROOT / "scripts"))

from expedition_hq_api import db as db_module
from expedition_hq_api.main import app
from expedition_hq_api.proposals import (
    DEFAULT_WORK_QUEUE_NOTE,
    normalize_implementation_route_plan,
    normalize_proposal,
    normalize_vote,
)
from expedition_hq_api.season import reconcile_season_state
from expedition_hq_api.xp import normalize_event_xp
from validate_seed import validate_schema_backed_seeds

def test_seed_json_loads():
    for path in (ROOT / "config").glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

def test_schema_backed_seed_files_match_core_schema():
    validate_schema_backed_seeds()

def test_agent_seed_has_coordinator():
    agents = json.loads((ROOT / "config" / "agent-roster.seed.json").read_text(encoding="utf-8"))
    assert any(a["id"] == "openclaw-main" for a in agents)

def test_season_policy_limits_rollover_to_xp_state():
    policy = json.loads((ROOT / "config" / "season-policy.seed.json").read_text(encoding="utf-8"))
    assert policy["reset_mode"] == "display_current_season_only"
    assert policy["scheduler_source_of_truth"] == "windows_task_scheduler"
    assert policy["codex_automation_role"] == "audit_report_only"
    assert policy["affected_domains"] == ["xp_current_season_display", "xp_season_state"]

    preserved = set(policy["preserve"])
    assert {
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
    }.issubset(preserved)

def test_season_rollover_writes_only_xp_state_file(tmp_path, monkeypatch):
    state_path = tmp_path / "season-state.json"
    monkeypatch.setenv("EXPEDITION_HQ_SEASON_STATE_PATH", str(state_path))

    result = reconcile_season_state(now="2026-05-30T06:30:00-07:00", write=True)

    assert result["state_path"] == str(state_path)
    assert state_path.exists()
    written_files = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file())
    assert written_files == ["season-state.json"]

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["affected_domains"] == ["xp_current_season_display", "xp_season_state"]
    assert "expeditions" in state["preserve"]
    assert "achievements" in state["preserve"]
    for non_xp_record_key in ["achievements", "milestones", "badges", "expeditions", "events", "field_reports"]:
        assert non_xp_record_key not in state

def test_codex_season_reset_audit_script_is_report_only():
    contents = (ROOT / "scripts" / "Audit-ExpeditionHQSeasonReset.ps1").read_text(encoding="utf-8")

    assert "audit_report_only" in contents
    assert "mutates_state = $false" in contents
    assert "Register-ScheduledTask" not in contents
    assert "Unregister-ScheduledTask" not in contents
    assert "Start-ScheduledTask" not in contents
    assert "Invoke-ExpeditionHQSeasonRollover.ps1 -Apply" not in contents

def test_archive_field_reports_reference_existing_seed_objects_and_artifacts():
    agents = json.loads((ROOT / "config" / "agent-roster.seed.json").read_text(encoding="utf-8"))
    expeditions = json.loads((ROOT / "config" / "expeditions.seed.json").read_text(encoding="utf-8"))
    agent_ids = {agent["id"] for agent in agents}
    expedition_ids = {expedition["id"] for expedition in expeditions}

    for report_path in sorted((ROOT / "archive" / "field-reports").glob("*.json")):
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report.get("source_id") in {*agent_ids, "manual"}
        assert report.get("expedition_id") in expedition_ids
        assert set(report.get("party_agents", [])).issubset(agent_ids)
        for artifact_ref in report.get("artifact_refs", []):
            artifact_path = (ROOT / artifact_ref).resolve()
            artifact_path.relative_to(ROOT)
            assert artifact_path.is_file()

@pytest.fixture()
def seeded_client(tmp_path, monkeypatch):
    monkeypatch.setenv("EXPEDITION_HQ_DB_PATH", str(tmp_path / "expedition-hq-test.db"))
    monkeypatch.setenv("EXPEDITION_HQ_SEASON_STATE_PATH", str(tmp_path / "season-state.json"))
    monkeypatch.setenv("EXPEDITION_HQ_IMPLEMENTATION_BRIEF_DIR", str(tmp_path / "implementation-briefs"))
    monkeypatch.setenv("EXPEDITION_HQ_IMPLEMENTATION_DISPATCH_DIR", str(tmp_path / "implementation-dispatch-jobs"))
    monkeypatch.setenv("EXPEDITION_HQ_NOW", "2026-05-28T02:00:00-07:00")
    importlib.reload(db_module)
    db_module.seed_db(force=True)
    with TestClient(app) as client:
        yield client

def test_required_endpoints_return_seeded_data(seeded_client):
    expected_counts = {
        "/agents": 25,
        "/expeditions": 6,
        "/events": 9,
        "/milestones": 5,
        "/incidents": 7,
        "/routes": 6,
        "/rooms": 8,
        "/route-edges": 6,
        "/memory-stores": 6,
        "/planned": 4,
        "/artifacts": 2,
        "/season-summaries": 1,
        "/proposals": 6,
    }

    health = seeded_client.get("/health")
    assert health.status_code == 200
    assert health.json()["mutation_policy"] == "local_sqlite_events_only"
    assert health.json()["local_writes_allowed"] is True
    assert health.json()["xp_season"] == "0.1"
    assert health.json()["season_window"]["daily_reset_time"] == "06:00"

    for path, minimum in expected_counts.items():
        response = seeded_client.get(path)
        assert response.status_code == 200
        assert len(response.json()) >= minimum

    incidents = seeded_client.get("/incidents").json()
    assert all(incident["status"] == "open" for incident in incidents)

def test_api_root_redirects_to_dashboard(seeded_client):
    response = seeded_client.get("/", follow_redirects=False)
    assert response.status_code in {302, 307}
    assert response.headers["location"] == "http://127.0.0.1:5173/"

def test_season_rollover_does_not_mutate_non_xp_records(seeded_client):
    preserved_tables = [
        "agents",
        "expeditions",
        "events",
        "milestones",
        "routes",
        "rooms",
        "artifacts",
        "season_summaries",
        "proposals",
    ]
    before = {table: db_module.rows(table) for table in preserved_tables}

    result = reconcile_season_state(now="2026-05-31T06:30:00-07:00", write=True)

    assert result["state"]["affected_domains"] == ["xp_current_season_display", "xp_season_state"]
    assert result["state"]["season"] == "0.2"
    after = {table: db_module.rows(table) for table in preserved_tables}
    assert after == before

def test_current_season_endpoint_uses_6am_window(seeded_client, monkeypatch):
    current = seeded_client.get("/season-current")
    assert current.status_code == 200
    payload = current.json()
    assert payload["season"] == "0.1"
    assert payload["status"] == "restart_pending"
    assert payload["next_reset_at"] == "2026-05-30T06:00:00-07:00"
    assert payload["scheduler_source_of_truth"] == "windows_task_scheduler"
    assert payload["codex_automation_role"] == "audit_report_only"
    assert payload["affected_domains"] == ["xp_current_season_display", "xp_season_state"]
    assert "expeditions" in payload["preserve"]
    assert "achievements" in payload["preserve"]
    assert payload["summary"]["event_count"] >= 9

    monkeypatch.setenv("EXPEDITION_HQ_NOW", "2026-05-30T06:30:00-07:00")
    restarted = seeded_client.get("/season-current")
    assert restarted.status_code == 200
    restarted_payload = restarted.json()
    assert restarted_payload["season"] == "0.1"
    assert restarted_payload["status"] == "active"
    assert restarted_payload["started_at"] == "2026-05-30T06:00:00-07:00"
    assert restarted_payload["summary"]["event_count"] == 0

    monkeypatch.setenv("EXPEDITION_HQ_NOW", "2026-05-31T06:30:00-07:00")
    next_season = seeded_client.get("/season-current").json()
    assert next_season["season"] == "0.2"
    assert next_season["started_at"] == "2026-05-31T06:00:00-07:00"

def test_season_participation_endpoint_aggregates_current_window(seeded_client):
    response = seeded_client.get("/season-participation")
    assert response.status_code == 200
    payload = response.json()

    assert payload["season"] == "0.1"
    assert payload["source_tables"] == ["events", "proposals"]
    assert payload["graphics_independent"] is True
    assert payload["activity_kinds"] == ["task", "goal", "proposal", "meaningful_action"]
    assert payload["tracking_started_at"] == "2026-05-27T19:55:33-07:00"
    assert payload["summary"]["meaningful_action_count"] >= 9
    assert payload["summary"]["goal_count"] >= 9
    assert payload["summary"]["proposal_count"] >= 6
    assert payload["summary"]["active_agent_count"] > 0
    assert {"approved", "work_queue", "actual_work", "final_review", "completed"}.issubset(
        payload["proposal_queue_counts"]
    )

    openclaw = next(agent for agent in payload["agents"] if agent["agent_id"] == "openclaw-main")
    assert openclaw["known_agent"] is True
    assert openclaw["awarded_xp"] > 0
    assert openclaw["roles"]["source"] > 0

def test_season_participation_starts_clean_at_initial_restart_without_losing_bureau_state(
    seeded_client,
    monkeypatch,
):
    monkeypatch.setenv("EXPEDITION_HQ_NOW", "2026-05-30T06:30:00-07:00")

    response = seeded_client.get("/season-participation")
    assert response.status_code == 200
    payload = response.json()

    assert payload["season"] == "0.1"
    assert payload["status"] == "active"
    assert payload["tracking_started_at"] == "2026-05-30T06:00:00-07:00"
    assert payload["summary"]["event_count"] == 0
    assert payload["summary"]["active_agent_count"] == 0
    assert payload["summary"]["meaningful_action_count"] == 0
    assert payload["proposal_queue_counts"]["completed"] >= 1
    assert payload["proposal_status_counts"]["accepted"] >= 1
    assert "approved" in payload["proposal_queue_counts"]
    assert "work_queue" in payload["proposal_queue_counts"]

def test_season_participation_tracks_new_task_goal_and_meaningful_action_after_restart(
    seeded_client,
    monkeypatch,
):
    monkeypatch.setenv("EXPEDITION_HQ_NOW", "2026-05-30T08:00:00-07:00")
    response = seeded_client.post(
        "/xp-claims",
        json={
            "id": "evt-season-0-1-task-claim",
            "timestamp": "2026-05-30T07:15:00-07:00",
            "source_id": "openclaw-main",
            "expedition_id": "expedition-hq-dashboard",
            "event_type": "task_completed",
            "title": "Season 0.1 task claim",
            "summary": "Records a reviewable task, goal link, and meaningful action after the Season 0.1 restart.",
            "active_minutes": 24,
            "evidence_refs": ["apps/api/tests/test_seed_files.py::test_season_participation_tracks_new_task_goal_and_meaningful_action_after_restart"],
            "tags": ["task", "season-0.1"],
        },
    )
    assert response.status_code == 200

    payload = seeded_client.get("/season-participation").json()
    assert payload["tracking_started_at"] == "2026-05-30T06:00:00-07:00"
    assert payload["summary"]["event_count"] == 1
    assert payload["summary"]["task_count"] == 1
    assert payload["summary"]["goal_count"] == 1
    assert payload["summary"]["meaningful_action_count"] == 1
    assert payload["summary"]["awarded_xp"] > 0

    openclaw = next(agent for agent in payload["agents"] if agent["agent_id"] == "openclaw-main")
    assert openclaw["task_count"] == 1
    assert openclaw["goal_count"] == 1
    assert openclaw["meaningful_action_count"] == 1
    assert openclaw["roles"]["source"] == 1

def test_retargeted_initial_restart_does_not_archive_warmup_state(tmp_path, monkeypatch):
    state_path = tmp_path / "season-state.json"
    state_path.write_text(json.dumps({
        "season": "0.1",
        "started_at": "2026-05-29T06:00:00-07:00",
        "status": "active",
        "reset_mode": "display_current_season_only",
        "history": [],
    }), encoding="utf-8")
    monkeypatch.setenv("EXPEDITION_HQ_SEASON_STATE_PATH", str(state_path))

    warmup = reconcile_season_state(now="2026-05-29T21:30:00-07:00", write=True)["state"]
    assert warmup["season"] == "0.1"
    assert warmup["status"] == "restart_pending"
    assert warmup["next_reset_at"] == "2026-05-30T06:00:00-07:00"
    assert warmup["history"] == []

    restarted = reconcile_season_state(now="2026-05-30T06:30:00-07:00", write=True)["state"]
    assert restarted["season"] == "0.1"
    assert restarted["status"] == "active"
    assert restarted["started_at"] == "2026-05-30T06:00:00-07:00"
    assert restarted["history"] == []

def test_public_seed_endpoint_is_not_available(seeded_client):
    response = seeded_client.post("/seed")
    assert response.status_code == 404

def test_world_map_and_activity_signals_are_available(seeded_client):
    world = seeded_client.get("/world-map")
    assert world.status_code == 200
    payload = world.json()
    assert len(payload["rooms"]) >= 8
    assert any(room["id"] == "staging-area" for room in payload["rooms"])
    assert any(edge["from_node_id"] == "comms-wing" for edge in payload["route_edges"])

    signals = seeded_client.get("/activity-signals")
    assert signals.status_code == 200
    openclaw = next(signal for signal in signals.json() if signal["agent_id"] == "openclaw-main")
    assert openclaw["latest_event_id"]
    assert openclaw["activity_reason"]

def test_local_write_gate_can_disable_event_ingest(seeded_client, monkeypatch):
    monkeypatch.setenv("EXPEDITION_HQ_ALLOW_WRITE_EVENTS", "false")
    response = seeded_client.post(
        "/events",
        json={
            "id": "evt-write-gate-disabled",
            "source_id": "openclaw-main",
            "expedition_id": "expedition-hq-dashboard",
            "event_type": "write_gate_probe",
            "title": "Write gate probe",
            "summary": "This local event should be rejected while write ingest is disabled.",
        },
    )
    assert response.status_code == 403

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
    assert openclaw["last_observed_at"]
    assert openclaw["latest_event_id"]
    assert openclaw["activity_reason"]
    assert openclaw["xp_status"]["peer_review_xp"] > 0
    assert openclaw["xp_status"]["peer_review_assessment_count"] > 0
    assert openclaw["xp_status"]["peer_review_scope"] == "current_season"
    assert openclaw["xp_status"]["peer_review_all_time"]["peer_review_xp"] >= openclaw["xp_status"]["peer_review_xp"]
    assert openclaw["xp_status"]["peer_review_all_time"]["peer_review_assessment_count"] >= openclaw["xp_status"]["peer_review_assessment_count"]


def test_peer_review_xp_respects_current_season_window(seeded_client, monkeypatch):
    monkeypatch.setenv("EXPEDITION_HQ_NOW", "2026-05-30T06:30:00-07:00")

    agents = seeded_client.get("/agents").json()
    openclaw = next(agent for agent in agents if agent["id"] == "openclaw-main")
    xp_status = openclaw["xp_status"]

    assert xp_status["peer_review_scope"] == "current_season"
    assert xp_status["peer_review_season"] == "0.1"
    assert xp_status["peer_review_window_started_at"] == "2026-05-30T06:00:00-07:00"
    assert xp_status["peer_review_window_ends_at"] == "2026-05-31T06:00:00-07:00"
    assert xp_status["peer_review_xp"] == 0
    assert xp_status["peer_review_assessment_count"] == 0
    assert xp_status["peer_review_all_time"]["peer_review_xp"] == 0.2
    assert xp_status["peer_review_all_time"]["peer_review_assessment_count"] == 5


def test_external_candidate_specialists_are_profiled_as_untrusted_visitors(seeded_client):
    agents = seeded_client.get("/agents").json()
    candidate_ids = {
        "copilot-visiting-specialist",
        "claude-visiting-specialist",
        "perplexity-visiting-specialist",
        "gemini-visiting-specialist",
        "deepseek-visiting-specialist",
        "kimi-visiting-specialist",
        "manus-visiting-specialist",
    }
    found = {agent["id"]: agent for agent in agents if agent["id"] in candidate_ids}

    assert set(found) == candidate_ids
    assert all(agent["visual_class"] == "candidate_specialist" for agent in found.values())
    assert all(agent["allowed_as_little_guy"] is True for agent in found.values())
    assert all(agent["candidate_profile"]["trust_level"] == "untrusted_candidate" for agent in found.values())
    assert all(agent["candidate_profile"]["free_tier_capabilities_profiled"] is False for agent in found.values())
    assert all(agent["candidate_profile"]["promotion_level"] == "unprofiled_candidate" for agent in found.values())
    assert all(agent["candidate_profile"]["promotion_recommendation"] == "needs_more_evidence" for agent in found.values())
    assert all("season_rollover" in agent["candidate_profile"]["promotion_review_cadence"] for agent in found.values())
    assert all(agent["candidate_profile"]["promotion_dossier"]["recommendation"] == "needs_more_evidence" for agent in found.values())
    assert all("implementer" not in agent["candidate_profile"]["allowed_roles"] for agent in found.values())


def test_candidate_promotion_recommendations_do_not_mutate_trust(seeded_client):
    agents = seeded_client.get("/agents").json()
    candidate = next(agent for agent in agents if agent["id"] == "claude-visiting-specialist")
    profile = candidate["candidate_profile"]

    assert profile["trust_level"] == "untrusted_candidate"
    assert profile["promotion_level"] == "unprofiled_candidate"
    assert profile["promotion_recommendation"] == "needs_more_evidence"
    assert profile["promotion_dossier"]["next_gate"]
    assert profile["evidence_refs"] == []


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
    assert proposal["broadcast_status"] == "broadcasted"
    assert "codex-memory-operator" in proposal["eligible_agent_ids"]
    assert proposal["council_summary"]["participation_count"] == proposal["council_summary"]["eligible_count"]
    assert proposal["council_summary"]["vote_counts"]["support"] == 2
    assert proposal["council_summary"]["vote_counts"]["abstain"] == proposal["council_summary"]["eligible_count"] - 2
    assert proposal["council_summary"]["healthy_abstain_count"] == proposal["council_summary"]["vote_counts"]["abstain"]
    assert proposal["council_summary"]["peer_review_participation_count"] == 3
    assert proposal["council_summary"]["amendment_requested_count"] == proposal["council_summary"]["eligible_count"] - 3
    assert "amendment requests" in proposal["council_summary"]["guidance"]
    assert {vote["agent_id"] for vote in proposal["council_votes"]} == set(proposal["eligible_agent_ids"])
    assert any(
        vote["response_kind"] == "required_abstain" and "amendment requested" in vote["reasoning"]
        for vote in proposal["council_votes"]
    )
    first_vote = proposal["council_votes"][0]
    assert first_vote["vote"] in {"support", "oppose", "abstain"}
    assert first_vote["reasoning"]
    assert first_vote["expected_benefit"]
    assert first_vote["expected_failure_mode"]
    assert first_vote["risk_notes"]

    missing = seeded_client.get("/proposals/proposal-does-not-exist")
    assert missing.status_code == 404


def test_legacy_work_start_note_reads_as_work_queue_next_step():
    proposal = proposal_payload("proposal-legacy-work-note", status="in_progress")
    proposal["work_started_at"] = "2026-05-29T19:53:34.549191+00:00"
    proposal["work_start_note"] = "Moved into the local work queue. No implementation automation is launched."

    normalized = normalize_proposal(proposal)

    assert normalized["work_start_note"] == DEFAULT_WORK_QUEUE_NOTE
    assert normalized["work_start_note_provided"] is False


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
    assert created["broadcast_status"] == "broadcasted"
    assert "openclaw-main" in created["eligible_agent_ids"]
    assert created["council_summary"]["participation_count"] == created["council_summary"]["eligible_count"]
    assert created["council_summary"]["vote_counts"]["abstain"] == created["council_summary"]["eligible_count"]
    assert created["council_summary"]["peer_review_participation_count"] == 0
    assert created["council_summary"]["amendment_requested_count"] == created["council_summary"]["eligible_count"]
    assert all(vote["response_kind"] == "required_abstain" for vote in created["council_votes"])
    assert all("peer-review XP" in vote["expected_benefit"] for vote in created["council_votes"])
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

def test_proposal_vote_endpoint_records_support_oppose_or_abstain(seeded_client):
    proposal_id = "proposal-vote-api"
    create = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
    assert create.status_code == 200

    vote_payload = {
        "agent_id": "openclaw-main",
        "vote": "abstain",
        "confidence": 0.25,
        "reasoning": "I do not know enough yet, so a careful specialist should not guess.",
        "expected_benefit": "Avoids fake certainty in council records.",
        "expected_failure_mode": "The proposal may wait for more context.",
        "risk_notes": "Low risk because abstain records uncertainty instead of action.",
        "context_notes": "API test vote.",
    }
    response = seeded_client.post(f"/proposals/{proposal_id}/votes", json=vote_payload)
    assert response.status_code == 200
    proposal = response.json()

    assert proposal["council_summary"]["participation_count"] == proposal["council_summary"]["eligible_count"]
    assert proposal["council_summary"]["vote_counts"]["abstain"] == proposal["council_summary"]["eligible_count"]
    assert proposal["council_summary"]["healthy_abstain_count"] == proposal["council_summary"]["eligible_count"]
    assert proposal["council_summary"]["peer_review_participation_count"] == 1
    assert proposal["council_summary"]["amendment_requested_count"] == proposal["council_summary"]["eligible_count"] - 1
    assert len([vote for vote in proposal["council_votes"] if vote["response_kind"] == "required_abstain"]) == proposal["council_summary"]["eligible_count"] - 1
    vote = next(vote for vote in proposal["council_votes"] if vote["agent_id"] == "openclaw-main")
    assert vote["agent_id"] == "openclaw-main"
    assert vote["vote"] == "abstain"
    assert vote["response_kind"] == "amended_after_prompt"
    assert vote["peer_review_xp_multiplier"] == 0.5
    assert "late-participation penalty" in vote["peer_review_xp_penalty_reason"]
    assert "Remember this next time" in vote["agent_memory_note"]
    assert "waiting for a nudge caps this review at half credit" in vote["context_notes"]
    assert vote["peer_review_xp"] == 0


def test_late_amended_useful_vote_is_capped_at_half_peer_review_xp():
    vote = normalize_vote({
        "vote_id": "vote-late-useful",
        "proposal_id": "proposal-late-useful",
        "agent_id": "openclaw-main",
        "vote": "support",
        "confidence": 0.8,
        "reasoning": "This is useful reasoning after a nudge.",
        "expected_benefit": "Makes the record useful.",
        "expected_failure_mode": "Late review should not earn full credit.",
        "risk_notes": "Penalty is for lateness, not correctness.",
        "usefulness_status": "useful",
        "peer_review_xp": 0.25,
        "response_kind": "amended_after_prompt",
    }, "proposal-late-useful")

    assert vote["peer_review_xp_multiplier"] == 0.5
    assert vote["peer_review_xp"] == 0.125


def test_proposal_vote_endpoint_rejects_ineligible_agent(seeded_client):
    proposal_id = "proposal-vote-ineligible"
    create = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
    assert create.status_code == 200

    response = seeded_client.post(
        f"/proposals/{proposal_id}/votes",
        json={
            "agent_id": "unknown-reviewer",
            "vote": "support",
            "confidence": 0.5,
            "reasoning": "Unknown agents cannot vote on a broadcast council item.",
            "expected_benefit": "No benefit.",
            "expected_failure_mode": "Bad records.",
            "risk_notes": "Should be rejected.",
        },
    )
    assert response.status_code == 400


def test_peer_review_xp_is_separate_from_work_xp(seeded_client):
    agents = seeded_client.get("/agents").json()
    openclaw = next(agent for agent in agents if agent["id"] == "openclaw-main")
    before_summary = seeded_client.get("/season-summaries").json()[0]

    assert openclaw["xp_status"]["peer_review_xp"] == 0.2
    assert openclaw["xp_status"]["peer_review_all_time"]["peer_review_xp"] == 0.2
    assert openclaw["xp_status"]["awarded_xp"] > openclaw["xp_status"]["peer_review_xp"]
    assert "peer_review_xp" not in before_summary

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

def test_approved_proposal_can_move_to_local_work_queue(seeded_client):
    proposal_id = "proposal-start-work"
    created = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
    assert created.status_code == 200
    approved = seeded_client.patch(
        f"/proposals/{proposal_id}/decision",
        json={"decision": "approve", "decision_note": "Approved for local work queue testing."},
    )
    assert approved.status_code == 200

    before = seeded_client.get("/season-summaries").json()[0]
    response = seeded_client.patch(
        f"/proposals/{proposal_id}/work-start",
        json={"start_note": "Start from tests and keep the action local."},
    )
    assert response.status_code == 200
    proposal = response.json()

    assert proposal["status"] == "in_progress"
    assert proposal["work_started_at"]
    assert proposal["work_start_note"] == "Start from tests and keep the action local."
    assert proposal["work_start_note_provided"] is True
    assert any(message["message_type"] == "work_start" for message in proposal["dialogue_messages"])

    events = seeded_client.get("/events").json()
    start_events = [
        event for event in events
        if event["event_type"] == "proposal_work_started" and event.get("proposal_id") == proposal_id
    ]
    assert len(start_events) == 1
    event = start_events[0]
    assert event["active_minutes"] == 0
    assert event["base_xp"] == 0
    assert event["awarded_xp"] == 0
    assert event["tags"] == ["proposal", "work-start", "local-only"]

    duplicate = seeded_client.patch(f"/proposals/{proposal_id}/work-start", json={})
    assert duplicate.status_code == 200
    events_after_duplicate = seeded_client.get("/events").json()
    duplicate_start_events = [
        event for event in events_after_duplicate
        if event["event_type"] == "proposal_work_started" and event.get("proposal_id") == proposal_id
    ]
    assert len(duplicate_start_events) == 1

    after = seeded_client.get("/season-summaries").json()[0]
    assert after["total_active_minutes"] == before["total_active_minutes"]
    assert after["total_base_xp"] == before["total_base_xp"]
    assert after["total_awarded_xp"] == before["total_awarded_xp"]


def test_queued_proposal_can_request_implementation_and_final_acceptance(seeded_client):
    proposal_id = "proposal-implementation-lifecycle"
    created = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
    assert created.status_code == 200
    approved = seeded_client.patch(
        f"/proposals/{proposal_id}/decision",
        json={"decision": "approve", "decision_note": "Approved for implementation lifecycle testing."},
    )
    assert approved.status_code == 200
    queued = seeded_client.patch(f"/proposals/{proposal_id}/work-start", json={})
    assert queued.status_code == 200

    requested = seeded_client.patch(
        f"/proposals/{proposal_id}/implementation-request",
        json={"request_note": "Route through the local OpenClaw/Codex implementation path."},
    )
    assert requested.status_code == 200
    proposal = requested.json()
    assert proposal["status"] == "implementation_requested"
    assert proposal["implementation_session_id"].startswith(f"impl-{proposal_id}-")
    assert proposal["implementation_dispatch_status"] == "queued"
    route_plan = proposal["implementation_route_plan"]
    assert route_plan["orchestration_layer"] == "OpenClaw"
    assert route_plan["route_snapshot_version"] == "provider_agnostic_v1"
    assert route_plan["primary_provider"] == "openclaw_router"
    assert route_plan["final_reviewer_id"] == "august"
    assert "implementer" in route_plan["provider_roles"]
    assert any(agent["task_role"] == "implementer" for agent in route_plan["selected_agents"])
    assert any(provider["provider"] == "Claude" for provider in route_plan["candidate_providers"])
    assert any(provider["unavailable_reason"] for provider in route_plan["skipped_providers"])
    brief_path = Path(proposal["implementation_brief_path"])
    assert brief_path.is_file()
    brief = brief_path.read_text(encoding="utf-8")
    assert f"# Implement Proposal: Proposal {proposal_id}" in brief
    assert "OpenClaw Routing Snapshot" in brief
    assert "Candidate providers:" in brief
    assert "Do not move this proposal to Completed directly." in brief
    dispatch_path = Path(route_plan["dispatch_job_path"])
    assert dispatch_path.is_file()
    dispatch_job = json.loads(dispatch_path.read_text(encoding="utf-8"))
    assert dispatch_job["job_type"] == "proposal_implementation"
    assert dispatch_job["route_snapshot"]["primary_provider"] == "openclaw_router"
    assert any(provider["provider"] == "DeepSeek" for provider in dispatch_job["skipped_providers"])

    events = seeded_client.get("/events").json()
    request_events = [
        event for event in events
        if event["event_type"] == "proposal_implementation_requested" and event.get("proposal_id") == proposal_id
    ]
    assert len(request_events) == 1
    assert request_events[0]["awarded_xp"] == 0
    assert request_events[0]["tags"] == ["proposal", "implementation-request", "local-only", "openclaw-routing"]

    completed = seeded_client.patch(
        f"/proposals/{proposal_id}/implementation-complete",
        json={
            "completion_note": "Implementation evidence is ready for final review.",
            "evidence_refs": ["npm.cmd run api:test", "npm.cmd run web:build"],
        },
    )
    assert completed.status_code == 200
    proposal = completed.json()
    assert proposal["status"] == "implemented"
    assert proposal["implementation_completed_at"]
    assert proposal["implementation_evidence_refs"] == ["npm.cmd run api:test", "npm.cmd run web:build"]

    review = seeded_client.patch(
        f"/proposals/{proposal_id}/implementation-review",
        json={
            "review_decision": "accept",
            "review_note": "Accepted after final review.",
            "reviewer_id": "august",
        },
    )
    assert review.status_code == 200
    proposal = review.json()
    assert proposal["status"] == "accepted"
    assert proposal["implementation_reviewer_id"] == "august"
    assert proposal["simulated_xp_gain"] == proposal["requested_xp_wager"]


def test_implementation_request_rejects_not_queued_proposal(seeded_client):
    proposal_id = "proposal-implementation-not-queued"
    created = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
    assert created.status_code == 200

    response = seeded_client.patch(f"/proposals/{proposal_id}/implementation-request", json={})

    assert response.status_code == 400
    assert "Only queued proposals" in response.json()["detail"]


def test_implementation_route_plan_accepts_unknown_candidate_providers():
    route_plan = normalize_implementation_route_plan({
        "orchestration_layer": "OpenClaw",
        "dispatch_mode": "openclaw_provider_agnostic",
        "selected_agents": [
            {
                "agent_id": "future-provider-specialist",
                "provider": "Future Provider",
                "access_mode": "free_or_manual_relay",
                "trust_level": "unprofiled_provider",
                "task_role": "research_crosscheck",
                "route_status": "candidate",
                "cost_quota_notes": "Profile free-tier value before trust.",
            }
        ],
        "candidate_providers": [
            {
                "agent_id": "unknown-critic",
                "provider": "Unknown Critic",
                "trust_level": "unprofiled_candidate",
                "task_role": "critic",
                "unavailable_reason": "Provider has not been attached yet.",
            }
        ],
    })

    assert route_plan["selected_agents"][0]["provider"] == "Future Provider"
    assert route_plan["selected_agents"][0]["trust_level"] == "unprofiled_provider"
    assert route_plan["candidate_providers"][0]["unavailable_reason"] == "Provider has not been attached yet."


def test_start_work_rejects_unapproved_proposal(seeded_client):
    proposal_id = "proposal-start-work-reject"
    created = seeded_client.post("/proposals", json=proposal_payload(proposal_id))
    assert created.status_code == 200

    response = seeded_client.patch(f"/proposals/{proposal_id}/work-start", json={})
    assert response.status_code == 400
    assert "Only approved, not-yet-started proposals" in response.json()["detail"]


def test_start_work_rejects_accepted_completed_proposal(seeded_client):
    response = seeded_client.patch("/proposals/proposal-council-review-mvp/work-start", json={})
    assert response.status_code == 400
    assert "Only approved, not-yet-started proposals" in response.json()["detail"]

    proposal = seeded_client.get("/proposals/proposal-council-review-mvp").json()
    assert proposal["status"] == "accepted"
    assert proposal["work_started_at"] is None

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

def test_proposal_backend_has_no_live_external_dispatch_calls():
    checked_files = [
        ROOT / "apps" / "api" / "expedition_hq_api" / "main.py",
        ROOT / "apps" / "api" / "expedition_hq_api" / "db.py",
        ROOT / "apps" / "api" / "expedition_hq_api" / "proposals.py",
    ]
    forbidden = [
        "hooks/agent",
        "codex exec",
        "Start-Process",
        "subprocess",
        "shell",
        "rotate_token",
        "token rotation",
        "token_REDACTED_FIELD_NAME",
        "Authorization",
        "Bearer ",
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
