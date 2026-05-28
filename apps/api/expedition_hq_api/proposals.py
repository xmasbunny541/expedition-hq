from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .xp import CURRENT_XP_SEASON, FORMULA_VERSION

PROPOSAL_STATUSES = {
    "draft",
    "pending",
    "approved",
    "denied",
    "revise_requested",
    "deferred",
    "implemented",
    "accepted",
    "rejected",
    "archived",
}
PROPOSAL_TYPES = {
    "polish",
    "discovery",
    "sentimental_record",
    "handoff_workflow",
    "gamification",
    "safety",
    "architecture",
}
DECISION_TO_STATUS = {
    "approve": "approved",
    "deny": "denied",
    "revise": "revise_requested",
    "defer": "deferred",
}


def normalize_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    out = dict(proposal)
    now = _now()
    status = out.get("status") or "pending"
    proposal_type = out.get("proposal_type") or "discovery"

    if status not in PROPOSAL_STATUSES:
        status = "pending"
    if proposal_type not in PROPOSAL_TYPES:
        proposal_type = "discovery"

    requested_wager = _non_negative(out.get("requested_xp_wager"), 0.0)
    simulated_gain = _non_negative(out.get("simulated_xp_gain"), 0.0)
    simulated_loss = _non_negative(out.get("simulated_xp_loss"), 0.0)
    if status == "accepted":
        simulated_gain = requested_wager
    if status == "denied":
        simulated_loss = requested_wager

    out["xp_season"] = out.get("xp_season") or CURRENT_XP_SEASON
    out["formula_version"] = out.get("formula_version") or FORMULA_VERSION
    out["proposal_type"] = proposal_type
    out["estimated_active_minutes"] = _non_negative(out.get("estimated_active_minutes"), 0.0)
    out["requested_xp_wager"] = requested_wager
    out["confidence"] = min(max(_non_negative(out.get("confidence"), 0.0), 0.0), 1.0)
    out["risk_level"] = out.get("risk_level") or "low"
    out["affected_areas"] = _string_list(out.get("affected_areas"))
    out["acceptance_criteria"] = _string_list(out.get("acceptance_criteria"))
    out["rollback_plan"] = out.get("rollback_plan") or ""
    out["status"] = status
    out["decision"] = out.get("decision")
    out["decision_note"] = out.get("decision_note")
    out["decided_at"] = out.get("decided_at")
    out["simulated_xp_gain"] = simulated_gain
    out["simulated_xp_loss"] = simulated_loss
    out["created_at"] = out.get("created_at") or now
    out["updated_at"] = out.get("updated_at") or out["created_at"]
    return out


def apply_decision(proposal: dict[str, Any], decision: str, decision_note: str) -> dict[str, Any]:
    out = normalize_proposal(proposal)
    status = DECISION_TO_STATUS[decision]
    requested_wager = _non_negative(out.get("requested_xp_wager"), 0.0)
    out["status"] = status
    out["decision"] = decision
    out["decision_note"] = decision_note
    out["decided_at"] = _now()
    out["updated_at"] = out["decided_at"]
    out["simulated_xp_gain"] = 0.0
    out["simulated_xp_loss"] = requested_wager if decision == "deny" else 0.0
    return out


def proposal_decision_event(proposal: dict[str, Any]) -> dict[str, Any]:
    decision = proposal.get("decision") or "unknown"
    wager = _non_negative(proposal.get("requested_xp_wager"), 0.0)
    loss = _non_negative(proposal.get("simulated_xp_loss"), 0.0)
    effect = f"simulated loss {loss:g} XP" if loss else "no simulated XP loss"
    timestamp = proposal.get("decided_at") or _now()
    return {
        "id": f"evt-proposal-{proposal['proposal_id']}-{decision}-{timestamp.replace(':', '').replace('.', '')}",
        "timestamp": timestamp,
        "source_id": "expedition-hq-dashboard",
        "expedition_id": "expedition-hq-dashboard",
        "event_type": "proposal_decision",
        "title": f"Proposal {decision}: {proposal['title']}",
        "summary": (
            f"{proposal['source_agent']} proposal '{proposal['title']}' was marked {proposal['status']}; "
            f"requested soft wager {wager:g} XP, {effect}."
        ),
        "status": "success",
        "risk_level": "low",
        "needs_review": False,
        "active_minutes": 0,
        "xp_confidence": "simulated",
        "party_agents": [],
        "scoring_multipliers": {
            "artifact": 1.0,
            "blocker_break": 1.0,
            "reuse_leverage": 1.0,
            "risk_control": 1.0,
        },
        "shadow_multipliers": {
            "discovery": False,
            "handoff_chain": False,
            "polish": False,
            "sentimental_record": False,
        },
        "multiplier_notes": [
            "Proposal decisions are local soft-wager records and do not apply real XP."
        ],
        "tags": ["proposal", "soft-wager", decision],
        "proposal_id": proposal["proposal_id"],
        "decision_note": proposal.get("decision_note"),
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _non_negative(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    return max(0.0, parsed)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
