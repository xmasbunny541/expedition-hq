from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .db import init_db, seed_db, rows, connect, insert_event, event_exists

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_db(force=False)
    yield

app = FastAPI(title="Expedition HQ API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
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
    xp: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list)

@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "expedition-hq-api",
        "mode": "read_only_with_local_event_ingest",
        "mutation_policy": "local_sqlite_events_only",
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
    with connect() as conn:
        if event_exists(conn, payload["id"]):
            raise HTTPException(status_code=409, detail=f"Event already exists: {payload['id']}")
        insert_event(conn, payload)
    return payload

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
