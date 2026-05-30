from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .proposals import normalize_proposal
from .season import current_season_window, event_in_window
from .xp import normalize_event_xp

TRACKED_ACTIVITY_KINDS = [
    "task",
    "goal",
    "proposal",
    "meaningful_action",
]

TASK_TAGS = {
    "task",
    "work",
    "implementation",
    "audit",
    "test",
    "build",
    "fix",
    "repair",
    "review",
    "handoff",
}


def aggregate_season_participation(
    events: list[dict[str, Any]],
    proposals: list[dict[str, Any]],
    known_agent_ids: set[str] | None = None,
    season_window: dict[str, Any] | None = None,
) -> dict[str, Any]:
    window = season_window or current_season_window()
    known_agents = set(known_agent_ids or set())
    agent_statuses: dict[str, dict[str, Any]] = {
        agent_id: _empty_agent_status(agent_id, known=True)
        for agent_id in sorted(known_agents)
    }
    summary = _empty_summary()
    recent_activity: list[dict[str, Any]] = []

    for event in events:
        normalized = normalize_event_xp(event)
        if not event_in_window(normalized, window):
            continue

        activity_kinds = event_activity_kinds(normalized)
        participants = event_participants(normalized)
        share_count = max(1, len(participants))
        active_minutes = _as_float(normalized.get("active_minutes"), 0.0)
        base_xp = _as_float(normalized.get("base_xp"), 0.0)
        awarded_xp = _as_float(normalized.get("awarded_xp"), 0.0)

        summary["event_count"] += 1
        summary["active_minutes"] += active_minutes
        summary["base_xp"] += base_xp
        summary["awarded_xp"] += awarded_xp
        if normalized.get("needs_review"):
            summary["review_item_count"] += 1
        for kind in activity_kinds:
            summary["activity_counts"][kind] += 1

        for agent_id in participants:
            status = agent_statuses.setdefault(
                agent_id,
                _empty_agent_status(agent_id, known=agent_id in known_agents),
            )
            status["event_count"] += 1
            status["active_minutes"] += active_minutes / share_count
            status["base_xp"] += base_xp / share_count
            status["awarded_xp"] += awarded_xp / share_count
            if normalized.get("needs_review"):
                status["review_item_count"] += 1
            for kind in activity_kinds:
                status["activity_counts"][kind] += 1
            _record_latest(status, normalized.get("timestamp"))

        source_id = str(normalized.get("source_id") or "").strip()
        if source_id:
            _add_agent_role(agent_statuses, source_id, "source", known_agents)
        for party_agent in normalized.get("party_agents") or []:
            _add_agent_role(agent_statuses, str(party_agent), "party", known_agents)

        recent_activity.append(_event_activity_record(normalized, activity_kinds, participants))

    normalized_proposals = [normalize_proposal(proposal) for proposal in proposals]
    proposal_status_counts = Counter(str(proposal.get("status") or "unknown") for proposal in normalized_proposals)
    proposal_queue_counts = {
        "approved": proposal_status_counts.get("approved", 0),
        "work_queue": proposal_status_counts.get("in_progress", 0),
        "actual_work": proposal_status_counts.get("implementation_requested", 0),
        "final_review": proposal_status_counts.get("implemented", 0),
        "completed": proposal_status_counts.get("accepted", 0),
    }

    for proposal in normalized_proposals:
        if _timestamp_in_window(proposal.get("created_at"), window):
            summary["proposal_record_count"] += 1
            summary["activity_counts"]["proposal"] += 1
            source_agent = str(proposal.get("source_agent") or "").strip()
            if source_agent:
                status = _add_agent_role(agent_statuses, source_agent, "proposal_author", known_agents)
                status["proposal_activity_count"] += 1
                _record_latest(status, proposal.get("created_at"))

        for vote in proposal.get("council_votes") or []:
            if vote.get("response_kind") == "required_abstain":
                continue
            if not _timestamp_in_window(vote.get("created_at"), window):
                continue
            agent_id = str(vote.get("agent_id") or "").strip()
            if not agent_id:
                continue
            summary["proposal_review_count"] += 1
            summary["activity_counts"]["proposal"] += 1
            summary["peer_review_xp"] += _as_float(vote.get("peer_review_xp"), 0.0)
            status = _add_agent_role(agent_statuses, agent_id, "proposal_reviewer", known_agents)
            status["proposal_activity_count"] += 1
            status["peer_review_xp"] += _as_float(vote.get("peer_review_xp"), 0.0)
            _record_latest(status, vote.get("created_at"))

        if _timestamp_in_window(proposal.get("implementation_requested_at"), window):
            route_plan = proposal.get("implementation_route_plan") or {}
            for selected in route_plan.get("selected_agents") or []:
                agent_id = str(selected.get("agent_id") or "").strip()
                if not agent_id:
                    continue
                status = _add_agent_role(agent_statuses, agent_id, "route_selected", known_agents)
                status["proposal_activity_count"] += 1
                _record_latest(status, proposal.get("implementation_requested_at"))

    agent_rows = [_finalize_agent_status(status) for status in agent_statuses.values()]
    active_agents = [
        agent for agent in agent_rows
        if agent["event_count"] or agent["proposal_activity_count"] or agent["awarded_xp"] or agent["peer_review_xp"]
    ]
    summary["active_agent_count"] = len(active_agents)

    return {
        "season": window["season"],
        "season_family": window["season_family"],
        "label": window["label"],
        "started_at": window["started_at"],
        "ends_at": window["ends_at"],
        "tracking_started_at": window["started_at"],
        "timezone": window["timezone"],
        "daily_reset_time": window["daily_reset_time"],
        "status": window["status"],
        "source_tables": ["events", "proposals"],
        "graphics_independent": True,
        "activity_kinds": TRACKED_ACTIVITY_KINDS,
        "summary": _finalize_summary(summary),
        "proposal_status_counts": dict(sorted(proposal_status_counts.items())),
        "proposal_queue_counts": proposal_queue_counts,
        "agents": sorted(
            active_agents,
            key=lambda agent: (
                agent["awarded_xp"] + agent["peer_review_xp"],
                agent["meaningful_action_count"] + agent["proposal_activity_count"],
                agent["latest_activity_at"],
            ),
            reverse=True,
        ),
        "recent_activity": sorted(
            recent_activity,
            key=lambda activity: activity.get("timestamp", ""),
            reverse=True,
        )[:12],
    }


def event_activity_kinds(event: dict[str, Any]) -> list[str]:
    tags = set(_string_list(event.get("tags")))
    event_type = str(event.get("event_type") or "").strip().lower()
    kinds: set[str] = set()

    if _is_task_event(event_type, tags):
        kinds.add("task")
    if event.get("expedition_id"):
        kinds.add("goal")
    if event_type.startswith("proposal_") or "proposal" in tags or event.get("proposal_id"):
        kinds.add("proposal")
    if _is_meaningful_action_event(event):
        kinds.add("meaningful_action")

    return [kind for kind in TRACKED_ACTIVITY_KINDS if kind in kinds]


def event_participants(event: dict[str, Any]) -> list[str]:
    participants: list[str] = []
    source_id = str(event.get("source_id") or "").strip()
    if source_id:
        participants.append(source_id)
    for agent_id in event.get("party_agents") or []:
        normalized = str(agent_id).strip()
        if normalized and normalized not in participants:
            participants.append(normalized)
    return participants


def _is_task_event(event_type: str, tags: set[str]) -> bool:
    normalized_tags = {tag.replace("-", "_") for tag in tags}
    if normalized_tags & TASK_TAGS:
        return True
    return any(hint in event_type for hint in ["task", "work", "implementation", "audit", "test", "build", "fix", "repair"])


def _is_meaningful_action_event(event: dict[str, Any]) -> bool:
    if _as_float(event.get("active_minutes"), 0.0) > 0:
        return True
    if event.get("field_report_path") or event.get("decision_record_ref") or event.get("test_output_ref"):
        return True
    if _string_list(event.get("evidence_refs")) or _string_list(event.get("artifact_refs")):
        return True
    if str(event.get("event_type") or "").startswith("proposal_"):
        return True
    return str(event.get("status") or "").strip() in {"success", "warning", "blocked", "review_pending"}


def _event_activity_record(
    event: dict[str, Any],
    activity_kinds: list[str],
    participants: list[str],
) -> dict[str, Any]:
    return {
        "record_type": "event",
        "id": event.get("id"),
        "timestamp": event.get("timestamp"),
        "title": event.get("title"),
        "event_type": event.get("event_type"),
        "expedition_id": event.get("expedition_id"),
        "activity_kinds": activity_kinds,
        "participants": participants,
        "active_minutes": _round(_as_float(event.get("active_minutes"), 0.0)),
        "awarded_xp": _round(_as_float(event.get("awarded_xp"), 0.0)),
        "needs_review": bool(event.get("needs_review")),
        "review_flags": _string_list(event.get("review_flags")),
    }


def _timestamp_in_window(timestamp: Any, window: dict[str, Any]) -> bool:
    if not timestamp:
        return False
    return event_in_window({"timestamp": str(timestamp)}, window)


def _add_agent_role(
    agent_statuses: dict[str, dict[str, Any]],
    agent_id: str,
    role: str,
    known_agent_ids: set[str],
) -> dict[str, Any]:
    normalized = str(agent_id or "").strip()
    status = agent_statuses.setdefault(
        normalized,
        _empty_agent_status(normalized, known=normalized in known_agent_ids),
    )
    status["roles"][role] += 1
    return status


def _record_latest(status: dict[str, Any], timestamp: Any) -> None:
    normalized = str(timestamp or "").strip()
    if normalized and normalized > status["latest_activity_at"]:
        status["latest_activity_at"] = normalized


def _empty_summary() -> dict[str, Any]:
    return {
        "active_agent_count": 0,
        "event_count": 0,
        "active_minutes": 0.0,
        "base_xp": 0.0,
        "awarded_xp": 0.0,
        "peer_review_xp": 0.0,
        "review_item_count": 0,
        "proposal_record_count": 0,
        "proposal_review_count": 0,
        "activity_counts": Counter({kind: 0 for kind in TRACKED_ACTIVITY_KINDS}),
    }


def _empty_agent_status(agent_id: str, known: bool) -> dict[str, Any]:
    return {
        "agent_id": agent_id,
        "known_agent": known,
        "event_count": 0,
        "proposal_activity_count": 0,
        "active_minutes": 0.0,
        "base_xp": 0.0,
        "awarded_xp": 0.0,
        "peer_review_xp": 0.0,
        "review_item_count": 0,
        "activity_counts": Counter({kind: 0 for kind in TRACKED_ACTIVITY_KINDS}),
        "roles": defaultdict(int),
        "latest_activity_at": "",
    }


def _finalize_summary(summary: dict[str, Any]) -> dict[str, Any]:
    activity_counts = dict(summary["activity_counts"])
    return {
        "active_agent_count": summary["active_agent_count"],
        "event_count": summary["event_count"],
        "active_minutes": _round(summary["active_minutes"]),
        "base_xp": _round(summary["base_xp"]),
        "awarded_xp": _round(summary["awarded_xp"]),
        "peer_review_xp": _round(summary["peer_review_xp"]),
        "review_item_count": summary["review_item_count"],
        "proposal_record_count": summary["proposal_record_count"],
        "proposal_review_count": summary["proposal_review_count"],
        "activity_counts": activity_counts,
        "task_count": activity_counts.get("task", 0),
        "goal_count": activity_counts.get("goal", 0),
        "proposal_count": activity_counts.get("proposal", 0),
        "meaningful_action_count": activity_counts.get("meaningful_action", 0),
    }


def _finalize_agent_status(status: dict[str, Any]) -> dict[str, Any]:
    activity_counts = dict(status["activity_counts"])
    roles = dict(sorted(status["roles"].items()))
    return {
        "agent_id": status["agent_id"],
        "known_agent": status["known_agent"],
        "event_count": status["event_count"],
        "proposal_activity_count": status["proposal_activity_count"],
        "active_minutes": _round(status["active_minutes"]),
        "base_xp": _round(status["base_xp"]),
        "awarded_xp": _round(status["awarded_xp"]),
        "peer_review_xp": _round(status["peer_review_xp"]),
        "review_item_count": status["review_item_count"],
        "activity_counts": activity_counts,
        "task_count": activity_counts.get("task", 0),
        "goal_count": activity_counts.get("goal", 0),
        "proposal_count": activity_counts.get("proposal", 0),
        "meaningful_action_count": activity_counts.get("meaningful_action", 0),
        "roles": roles,
        "latest_activity_at": status["latest_activity_at"],
    }


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: float) -> float:
    return round(float(value), 6)
