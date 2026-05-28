from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .db import (
    init_db,
    seed_db,
    rows,
    connect,
    insert_event,
    event_exists,
    insert_proposal,
    proposal_by_id,
    proposal_exists,
    season_summary_rows,
    update_proposal_decision,
)
from .xp import CURRENT_XP_LABEL, CURRENT_XP_SEASON, FORMULA_VERSION, XP_MODE, normalize_event_xp

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

class EventIn(BaseModel):
    id: str | None = Field(default=None, min_length=1)
    timestamp: str | None = None
    source_id: str = Field(min_length=1)
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
    decision_note: str = Field(min_length=1)

@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "expedition-hq-api",
        "mode": "read_only_with_local_event_ingest",
        "mutation_policy": "local_sqlite_events_only",
        "xp_season": CURRENT_XP_SEASON,
        "formula_version": FORMULA_VERSION,
        "xp_mode": XP_MODE,
        "xp_label": CURRENT_XP_LABEL,
    }

@app.get("/agents")
def agents() -> list[dict[str, Any]]:
    return rows("agents")

@app.get("/expeditions")
def expeditions() -> list[dict[str, Any]]:
    return rows("expeditions")

@app.get("/events")
def events() -> list[dict[str, Any]]:
    return sorted(rows("events"), key=lambda e: e.get("timestamp", ""), reverse=True)

@app.post("/events")
def create_event(event: EventIn) -> dict[str, Any]:
    payload = event.model_dump()
    payload["id"] = payload["id"] or f"evt-{uuid4().hex[:12]}"
    payload["timestamp"] = payload["timestamp"] or datetime.now(timezone.utc).isoformat()
    payload = normalize_event_xp(payload)
    with connect() as conn:
        if event_exists(conn, payload["id"]):
            raise HTTPException(status_code=409, detail=f"Event already exists: {payload['id']}")
        insert_event(conn, payload)
    return payload

@app.get("/proposals")
def proposals() -> list[dict[str, Any]]:
    return sorted(rows("proposals"), key=lambda p: p.get("created_at", ""), reverse=True)

@app.get("/proposals/{proposal_id}")
def proposal(proposal_id: str) -> dict[str, Any]:
    found = proposal_by_id(proposal_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
    return found

@app.post("/proposals")
def create_proposal(proposal: ProposalIn) -> dict[str, Any]:
    payload = proposal.model_dump()
    payload["proposal_id"] = payload["proposal_id"] or f"proposal-{uuid4().hex[:12]}"
    payload["xp_season"] = CURRENT_XP_SEASON
    payload["formula_version"] = FORMULA_VERSION
    with connect() as conn:
        if proposal_exists(conn, payload["proposal_id"]):
            raise HTTPException(status_code=409, detail=f"Proposal already exists: {payload['proposal_id']}")
        return insert_proposal(conn, payload)

@app.patch("/proposals/{proposal_id}/decision")
def decide_proposal(proposal_id: str, decision: ProposalDecisionIn) -> dict[str, Any]:
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

@app.get("/milestones")
def milestones() -> list[dict[str, Any]]:
    return rows("milestones")

@app.get("/incidents")
def incidents() -> list[dict[str, Any]]:
    return rows("incidents")

@app.get("/routes")
def routes() -> list[dict[str, Any]]:
    return rows("routes")

@app.get("/memory-stores")
def memory_stores() -> list[dict[str, Any]]:
    return rows("memory_stores")

@app.get("/planned")
def planned() -> list[dict[str, Any]]:
    return rows("planned_items")

@app.get("/artifacts")
def artifacts() -> list[dict[str, Any]]:
    return rows("artifacts")

@app.get("/season-summaries")
def season_summaries() -> list[dict[str, Any]]:
    return season_summary_rows()
