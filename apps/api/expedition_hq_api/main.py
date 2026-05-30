from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field

from .db import (
    ROOT,
    init_db,
    seed_db,
    rows,
    connect,
    insert_event,
    event_exists,
    insert_proposal,
    proposal_by_id,
    proposal_exists,
    proposal_rows,
    season_summary_rows,
    update_proposal_decision,
    update_proposal_implementation_complete,
    update_proposal_implementation_request,
    update_proposal_implementation_review,
    update_proposal_vote,
    update_proposal_work_start,
)
from .proposals import aggregate_peer_review_status
from .season import current_season_window, filter_events_for_window
from .xp import (
    FORMULA_VERSION,
    XP_MODE,
    aggregate_season_summary,
    aggregate_agent_xp_status,
    audit_event_claim,
    audit_event_claims,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_db(force=False)
    yield

app = FastAPI(title="Expedition HQ API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        "http://127.0.0.1:5175",
        "http://localhost:5175",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
    allow_origin_regex=r"http://(127\.0\.0\.1|localhost):517[3-9]",
)

WRITE_DISABLED_VALUES = {"0", "false", "no", "off"}
DASHBOARD_URL = os.environ.get("EXPEDITION_HQ_WEB_URL", "http://127.0.0.1:5173/").strip() or "http://127.0.0.1:5173/"


@app.get("/", include_in_schema=False)
def dashboard_redirect() -> RedirectResponse:
    return RedirectResponse(DASHBOARD_URL)


def local_writes_allowed() -> bool:
    return os.environ.get("EXPEDITION_HQ_ALLOW_WRITE_EVENTS", "true").strip().lower() not in WRITE_DISABLED_VALUES


def require_local_writes() -> None:
    if not local_writes_allowed():
        raise HTTPException(
            status_code=403,
            detail="Local ledger writes are disabled by EXPEDITION_HQ_ALLOW_WRITE_EVENTS.",
        )


def audited_events() -> list[dict[str, Any]]:
    known_agent_ids = {agent["id"] for agent in rows("agents")}
    audited = audit_event_claims(rows("events"), known_agent_ids=known_agent_ids)
    return sorted(audited, key=lambda e: e.get("timestamp", ""), reverse=True)


def latest_event_for_agent(agent: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any] | None:
    agent_id = agent["id"]
    assignment = agent.get("current_assignment")
    for event in events:
        if (
            event.get("source_id") == agent_id
            or agent_id in (event.get("party_agents") or [])
            or (assignment and event.get("expedition_id") == assignment)
        ):
            return event
    return None


def agent_activity_signal(agent: dict[str, Any], event: dict[str, Any] | None) -> dict[str, Any]:
    xp_status = agent.get("xp_status") or {}
    return {
        "agent_id": agent["id"],
        "display_name": agent.get("visual_name") or agent.get("display_name"),
        "ui_state": agent.get("ui_state"),
        "room": agent.get("room"),
        "current_assignment": agent.get("current_assignment"),
        "latest_event_id": event.get("id") if event else None,
        "latest_event_title": event.get("title") if event else None,
        "latest_event_at": event.get("timestamp") if event else xp_status.get("latest_event_at", ""),
        "activity_reason": event.get("summary") if event else agent.get("summary"),
        "needs_review": bool(event and event.get("needs_review")),
        "risk_level": event.get("risk_level") if event else "low",
        "review_flags": event.get("review_flags", []) if event else [],
    }


TRUST_LADDER = [
    "unprofiled_candidate",
    "profiled_candidate",
    "trusted_reviewer",
    "limited_implementer",
    "trusted_implementer",
]
ROLE_BY_TRUST_LEVEL = {
    "unprofiled_candidate": ["research_crosscheck", "critic", "cheap_reasoning_check"],
    "profiled_candidate": ["research_crosscheck", "source_checker", "critic", "cheap_reasoning_check"],
    "trusted_reviewer": ["research_crosscheck", "source_checker", "critic"],
    "limited_implementer": ["critic", "implementer", "source_checker"],
    "trusted_implementer": ["implementer", "critic", "final_synthesizer"],
}


def candidate_profile_with_promotion(agent: dict[str, Any], xp_status: dict[str, Any]) -> dict[str, Any] | None:
    profile = dict(agent.get("candidate_profile") or {})
    if not profile:
        return None

    current_level = str(profile.get("promotion_level") or "").strip()
    if current_level not in TRUST_LADDER:
        current_level = "profiled_candidate" if profile.get("free_tier_capabilities_profiled") else "unprofiled_candidate"

    useful_outputs = int(profile.get("useful_output_count") or xp_status.get("peer_review_useful_count") or 0)
    safety_flags = [str(flag).strip() for flag in profile.get("safety_flags", []) if str(flag).strip()]
    recommendation = str(profile.get("promotion_recommendation") or "").strip()
    if not recommendation:
        if safety_flags:
            recommendation = "hold"
        elif current_level == "profiled_candidate" and useful_outputs >= 3:
            recommendation = "promote"
        else:
            recommendation = "needs_more_evidence"

    evidence_refs = [str(ref).strip() for ref in profile.get("evidence_refs", []) if str(ref).strip()]
    pros = profile.get("promotion_pros") or [
        "Can improve cross-reference coverage and reduce trusted Codex token pressure when privacy allows.",
    ]
    cons = profile.get("promotion_cons") or [
        "Not trusted for repo edits, private context, or implementation evidence until local results prove safe.",
    ]
    next_gate = str(profile.get("next_promotion_gate") or profile.get("promotion_gate") or "").strip() or (
        "Record useful, safe, redacted outputs across a season review window before expanding permissions."
    )

    profile.update({
        "promotion_level": current_level,
        "trust_ladder": TRUST_LADDER,
        "allowed_roles": profile.get("allowed_roles") or ROLE_BY_TRUST_LEVEL[current_level],
        "restrictions": profile.get("restrictions") or [
            "No secrets or raw private transcripts.",
            "No trusted repo edits until promoted to limited_implementer.",
            "Candidate output supports cross-reference only until promoted.",
        ],
        "safety_flags": safety_flags,
        "useful_output_count": useful_outputs,
        "evidence_refs": evidence_refs,
        "availability_notes": profile.get("availability_notes") or "Use only when OpenClaw reports this provider as available.",
        "cost_quota_notes": profile.get("cost_quota_notes") or "Prefer free or cheap quota for cross-check work before spending trusted Codex time.",
        "promotion_review_cadence": profile.get("promotion_review_cadence") or (
            "season_rollover; midpoint only for longer seasons"
        ),
        "promotion_recommendation": recommendation,
        "promotion_dossier": {
            "pros": pros,
            "cons": cons,
            "recommendation": recommendation,
            "next_gate": next_gate,
            "evidence": evidence_refs,
        },
    })
    return profile

class EventIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None, min_length=1)
    timestamp: str | None = None
    source_id: str = Field(min_length=1)
    source_project: str | None = None
    expedition_id: str | None = None
    event_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    status: str = Field(default="success", min_length=1)
    risk_level: str = Field(default="low", min_length=1)
    needs_review: bool = False
    active_minutes: float = Field(default=0, ge=0)
    xp_confidence: str = Field(default="estimated", min_length=1)
    party_agents: list[str] = Field(default_factory=list)
    scoring_multipliers: dict[str, float] = Field(default_factory=dict)
    shadow_multipliers: dict[str, bool] = Field(default_factory=dict)
    shadow_multiplier_notes: str | list[str] = Field(default_factory=list)
    multiplier_notes: str | list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    artifact_refs: list[str] = Field(default_factory=list)
    field_report_path: str | None = None
    decision_record_ref: str | None = None
    test_output_ref: str | None = None
    tags: list[str] = Field(default_factory=list)

class ProposalIn(BaseModel):
    proposal_id: str | None = Field(default=None, min_length=1)
    source_agent: str = Field(min_length=1)
    proposal_type: Literal[
        "polish",
        "discovery",
        "sentimental_record",
        "handoff_workflow",
        "gamification",
        "safety",
        "architecture",
    ]
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    reasoning: str = Field(min_length=1)
    estimated_active_minutes: float = Field(default=0, ge=0)
    requested_xp_wager: float = Field(default=0, ge=0)
    confidence: float = Field(default=0, ge=0, le=1)
    risk_level: str = Field(default="low", min_length=1)
    affected_areas: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    rollback_plan: str = Field(min_length=1)
    status: Literal["draft", "pending"] = "pending"

class ProposalDecisionIn(BaseModel):
    decision: Literal["approve", "deny", "revise", "defer"]
    decision_note: str | None = None

class ProposalVoteIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vote_id: str | None = Field(default=None, min_length=1)
    agent_id: str = Field(min_length=1)
    vote: Literal["support", "oppose", "abstain"]
    confidence: float = Field(ge=0, le=1)
    reasoning: str = Field(min_length=1)
    expected_benefit: str = Field(min_length=1)
    expected_failure_mode: str = Field(min_length=1)
    risk_notes: str = Field(min_length=1)
    context_notes: str | None = None

class ProposalWorkStartIn(BaseModel):
    start_note: str | None = None

class ProposalImplementationRequestIn(BaseModel):
    request_note: str | None = None

class ProposalImplementationCompleteIn(BaseModel):
    completion_note: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)

class ProposalImplementationReviewIn(BaseModel):
    review_decision: Literal["accept", "reject"]
    review_note: str | None = None
    reviewer_id: str | None = "august"

@app.get("/health")
def health() -> dict[str, Any]:
    season_window = current_season_window()
    return {
        "ok": True,
        "service": "expedition-hq-api",
        "mode": "read_only_with_local_event_ingest",
        "mutation_policy": "local_sqlite_events_only",
        "local_writes_allowed": local_writes_allowed(),
        "xp_season": season_window["season"],
        "formula_version": FORMULA_VERSION,
        "xp_mode": XP_MODE,
        "xp_label": season_window["label"],
        "season_window": season_window,
    }

@app.get("/agents")
def agents() -> list[dict[str, Any]]:
    agent_rows = rows("agents")
    known_agent_ids = {agent["id"] for agent in agent_rows}
    events_by_recency = audited_events()
    xp_statuses = aggregate_agent_xp_status(
        events_by_recency,
        known_agent_ids,
        season_window=current_season_window(),
    )
    peer_review_statuses = aggregate_peer_review_status(
        proposal_rows(),
        known_agent_ids,
        season_window=current_season_window(),
    )
    out = []
    for agent in agent_rows:
        xp_status = {
            **(xp_statuses.get(agent["id"]) or {}),
            **(peer_review_statuses.get(agent["id"]) or {}),
        }
        event = latest_event_for_agent(agent, events_by_recency)
        signal = agent_activity_signal({**agent, "xp_status": xp_status}, event)
        agent_out = {
            **agent,
            "xp_status": xp_status,
            "last_observed_at": signal["latest_event_at"],
            "latest_event_id": signal["latest_event_id"],
            "latest_event_title": signal["latest_event_title"],
            "activity_reason": signal["activity_reason"],
        }
        candidate_profile = candidate_profile_with_promotion(agent_out, xp_status)
        if candidate_profile:
            agent_out["candidate_profile"] = candidate_profile
        out.append(agent_out)
    return out

@app.get("/expeditions")
def expeditions() -> list[dict[str, Any]]:
    return rows("expeditions")

@app.get("/events")
def events() -> list[dict[str, Any]]:
    return audited_events()

@app.post("/events")
def create_event(event: EventIn) -> dict[str, Any]:
    return create_xp_claim_event(event)

@app.post("/xp-claims")
def create_xp_claim(event: EventIn) -> dict[str, Any]:
    return create_xp_claim_event(event)

def create_xp_claim_event(event: EventIn) -> dict[str, Any]:
    require_local_writes()
    payload = event.model_dump()
    payload["id"] = payload["id"] or f"evt-{uuid4().hex[:12]}"
    payload["timestamp"] = payload["timestamp"] or datetime.now(timezone.utc).isoformat()
    known_agent_ids = {agent["id"] for agent in rows("agents")}
    existing_events = rows("events")
    payload = audit_event_claim(payload, known_agent_ids=known_agent_ids, existing_events=existing_events)
    with connect() as conn:
        if event_exists(conn, payload["id"]):
            raise HTTPException(status_code=409, detail=f"Event already exists: {payload['id']}")
        insert_event(conn, payload)
    return payload

@app.get("/proposals")
def proposals() -> list[dict[str, Any]]:
    return sorted(proposal_rows(), key=lambda p: p.get("created_at", ""), reverse=True)

@app.get("/proposals/{proposal_id}")
def proposal(proposal_id: str) -> dict[str, Any]:
    found = proposal_by_id(proposal_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
    return found

@app.post("/proposals")
def create_proposal(proposal: ProposalIn) -> dict[str, Any]:
    require_local_writes()
    payload = proposal.model_dump()
    payload["proposal_id"] = payload["proposal_id"] or f"proposal-{uuid4().hex[:12]}"
    payload["xp_season"] = current_season_window()["season"]
    payload["formula_version"] = FORMULA_VERSION
    with connect() as conn:
        if proposal_exists(conn, payload["proposal_id"]):
            raise HTTPException(status_code=409, detail=f"Proposal already exists: {payload['proposal_id']}")
        return insert_proposal(conn, payload)

@app.patch("/proposals/{proposal_id}/decision")
def decide_proposal(proposal_id: str, decision: ProposalDecisionIn) -> dict[str, Any]:
    require_local_writes()
    with connect() as conn:
        updated = update_proposal_decision(
            conn,
            proposal_id,
            decision.decision,
            decision.decision_note,
        )
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
    return updated

@app.post("/proposals/{proposal_id}/votes")
def cast_proposal_vote(proposal_id: str, vote: ProposalVoteIn) -> dict[str, Any]:
    require_local_writes()
    with connect() as conn:
        try:
            updated = update_proposal_vote(conn, proposal_id, vote.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
    return updated

@app.patch("/proposals/{proposal_id}/work-start")
def start_proposal_work(proposal_id: str, work_start: ProposalWorkStartIn) -> dict[str, Any]:
    require_local_writes()
    with connect() as conn:
        try:
            updated = update_proposal_work_start(conn, proposal_id, work_start.start_note)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
    return updated

@app.patch("/proposals/{proposal_id}/implementation-request")
def request_proposal_implementation(
    proposal_id: str,
    implementation_request: ProposalImplementationRequestIn,
) -> dict[str, Any]:
    require_local_writes()
    with connect() as conn:
        try:
            updated = update_proposal_implementation_request(
                conn,
                proposal_id,
                implementation_request.request_note,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
    return updated

@app.patch("/proposals/{proposal_id}/implementation-complete")
def complete_proposal_implementation(
    proposal_id: str,
    implementation_complete: ProposalImplementationCompleteIn,
) -> dict[str, Any]:
    require_local_writes()
    with connect() as conn:
        try:
            updated = update_proposal_implementation_complete(
                conn,
                proposal_id,
                implementation_complete.completion_note,
                implementation_complete.evidence_refs,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
    return updated

@app.patch("/proposals/{proposal_id}/implementation-review")
def review_proposal_implementation(
    proposal_id: str,
    implementation_review: ProposalImplementationReviewIn,
) -> dict[str, Any]:
    require_local_writes()
    with connect() as conn:
        try:
            updated = update_proposal_implementation_review(
                conn,
                proposal_id,
                implementation_review.review_decision,
                implementation_review.review_note,
                implementation_review.reviewer_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
    return updated

@app.get("/milestones")
def milestones() -> list[dict[str, Any]]:
    return rows("milestones")

@app.get("/incidents")
def incidents() -> list[dict[str, Any]]:
    return rows("incidents")

@app.get("/routes")
def routes() -> list[dict[str, Any]]:
    return rows("routes")

@app.get("/rooms")
def rooms() -> list[dict[str, Any]]:
    return sorted(rows("rooms"), key=lambda room: room.get("sort_order", 0))

@app.get("/route-edges")
def route_edges() -> list[dict[str, Any]]:
    return rows("route_edges")

@app.get("/activity-signals")
def activity_signals() -> list[dict[str, Any]]:
    event_rows = audited_events()
    return [
        agent_activity_signal(agent, latest_event_for_agent(agent, event_rows))
        for agent in agents()
    ]

@app.get("/world-map")
def world_map() -> dict[str, Any]:
    return {
        "rooms": rooms(),
        "route_edges": route_edges(),
        "agents": agents(),
        "routes": routes(),
        "incidents": rows("incidents"),
        "recent_events": events()[:12],
    }

@app.get("/dashboard-config")
def dashboard_config() -> dict[str, Any]:
    config_path = ROOT / "config" / "dashboard.config.example.json"
    if not config_path.exists():
        return {"refresh_seconds": 15, "redaction_required": True}
    import json

    return json.loads(config_path.read_text(encoding="utf-8"))

@app.get("/memory-stores")
def memory_stores() -> list[dict[str, Any]]:
    return rows("memory_stores")

@app.get("/planned")
def planned() -> list[dict[str, Any]]:
    return rows("planned_items")

@app.get("/artifacts")
def artifacts() -> list[dict[str, Any]]:
    return rows("artifacts")

@app.get("/season-current")
def season_current() -> dict[str, Any]:
    window = current_season_window()
    current_events = filter_events_for_window(audited_events(), window)
    summary = aggregate_season_summary(
        current_events,
        {
            "season": window["season"],
            "formula_version": window["formula_version"],
            "xp_mode": window["xp_mode"],
            "label": window["label"],
            "started_at": window["started_at"],
            "ended_at": None,
            "notes": [
                "Current-season totals are filtered to the active 6am-to-6am window.",
                "Historical events remain in the ledger and season summaries.",
            ],
        },
    )
    return {
        **window,
        "summary": summary,
        "event_count": summary["event_count"],
    }

@app.get("/season-summaries")
def season_summaries() -> list[dict[str, Any]]:
    return season_summary_rows()
