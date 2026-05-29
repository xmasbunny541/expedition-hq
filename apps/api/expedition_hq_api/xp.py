from __future__ import annotations

from collections import Counter, defaultdict
from math import prod
from typing import Any

CURRENT_XP_SEASON = "0.1"
CURRENT_XP_LABEL = "Season 0.x · Uncapped Calibration XP"
FORMULA_VERSION = "xp_calibration_v0_1"
XP_MODE = "uncapped_calibration"
XP_SOURCE = "active_minutes"

SCORING_MULTIPLIERS = [
    "grinding",
    "party_size",
    "artifact",
    "blocker_break",
    "reuse_leverage",
    "risk_control",
]
SHADOW_MULTIPLIERS = [
    "discovery",
    "handoff_chain",
    "polish",
    "sentimental_record",
]
XP_CLAIM_STATUS_AWARDED = "calibration_awarded"
XP_CLAIM_STATUS_REVIEW_PENDING = "review_pending"
XP_CLAIM_STATUS_ZERO = "zero_xp_record"

ALLOWED_SCORING_VALUES: dict[str, set[float]] = {
    "artifact": {1.0, 1.15, 1.3},
    "blocker_break": {1.0, 1.1, 1.5},
    "reuse_leverage": {1.0, 1.3, 2.0},
    "risk_control": {1.0, 1.25},
}


def grinding_multiplier(active_minutes: float) -> float:
    if active_minutes < 10:
        return 1.0
    if active_minutes < 30:
        return 1.1
    if active_minutes < 60:
        return 1.25
    return 1.5


def party_size_multiplier(party_size: int) -> float:
    return min(1.0 + max(0, party_size) * 0.1, 1.5)


def normalize_event_xp(event: dict[str, Any]) -> dict[str, Any]:
    out = dict(event)
    active_minutes = max(0.0, _as_float(out.get("active_minutes"), 0.0))
    party_agents = _unique_agent_ids(out.get("party_agents"), out.get("source_id"))
    party_size = len(party_agents)

    scoring_input = out.get("scoring_multipliers")
    if not isinstance(scoring_input, dict):
        scoring_input = {}

    scoring_multipliers = {
        "grinding": grinding_multiplier(active_minutes),
        "party_size": party_size_multiplier(party_size),
        "artifact": _allowed_multiplier("artifact", scoring_input.get("artifact")),
        "blocker_break": _allowed_multiplier("blocker_break", scoring_input.get("blocker_break")),
        "reuse_leverage": _allowed_multiplier("reuse_leverage", scoring_input.get("reuse_leverage")),
        "risk_control": _allowed_multiplier("risk_control", scoring_input.get("risk_control")),
    }

    total_multiplier_raw = prod(scoring_multipliers.values())
    base_xp = active_minutes / 60
    awarded_xp = base_xp * total_multiplier_raw

    out["xp_season"] = out.get("xp_season") or CURRENT_XP_SEASON
    out["formula_version"] = FORMULA_VERSION
    out["xp_mode"] = XP_MODE
    out["active_minutes"] = _round(active_minutes)
    out["base_xp"] = _round(base_xp)
    out["awarded_xp"] = _round(awarded_xp)
    out["xp"] = out["awarded_xp"]
    out["total_multiplier_raw"] = _round(total_multiplier_raw)
    out["multiplier_cap"] = None
    out["xp_source"] = XP_SOURCE
    out["xp_confidence"] = out.get("xp_confidence") or "estimated"
    out["party_agents"] = party_agents
    out["party_size"] = party_size
    out["source_project"] = _optional_string(out.get("source_project"))
    out["evidence_refs"] = _string_list(out.get("evidence_refs"))
    out["artifact_refs"] = _string_list(out.get("artifact_refs"))
    out["field_report_path"] = _optional_string(out.get("field_report_path"))
    out["decision_record_ref"] = _optional_string(out.get("decision_record_ref"))
    out["test_output_ref"] = _optional_string(out.get("test_output_ref"))
    out["scoring_multipliers"] = {key: _round(scoring_multipliers[key]) for key in SCORING_MULTIPLIERS}
    out["shadow_multipliers"] = _normalize_shadow_multipliers(out.get("shadow_multipliers"))
    out["shadow_multiplier_notes"] = out.get("shadow_multiplier_notes", [])
    out["multiplier_notes"] = out.get("multiplier_notes", [])
    out["scaling_flags"] = scaling_flags(base_xp, awarded_xp, total_multiplier_raw)
    out["review_flags"] = review_flags(out)
    out["needs_review"] = _needs_review(out)
    out["xp_claim_status"] = xp_claim_status(out)
    return out


def scaling_flags(base_xp: float, awarded_xp: float, total_multiplier_raw: float) -> list[str]:
    flags: list[str] = []
    if total_multiplier_raw >= 3.0:
        flags.append("high_multiplier")
    if total_multiplier_raw >= 5.0:
        flags.append("extreme_multiplier")
    if base_xp > 0 and awarded_xp >= base_xp * 5:
        flags.append("scaling_review")
    return flags


def review_flags(event: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    _append_unique(flags, _string_list(event.get("review_flags")))
    _append_unique(flags, _string_list(event.get("scaling_flags")))

    active_minutes = _as_float(event.get("active_minutes"), 0.0)
    summary = str(event.get("summary") or "").strip()

    if active_minutes > 0 and not _has_evidence(event):
        flags.append("missing_evidence")
    if active_minutes > 0 and not event.get("expedition_id"):
        flags.append("missing_expedition")
    if active_minutes >= 120:
        flags.append("large_active_minutes")
    if 0 < active_minutes < 5:
        flags.append("tiny_claim")
    if active_minutes > 0 and len(summary) < 40:
        flags.append("thin_summary")
    if int(event.get("party_size") or 0) >= 4:
        flags.append("large_party_claim")

    return _dedupe(flags)


def audit_event_claim(
    event: dict[str, Any],
    known_agent_ids: set[str] | None = None,
    existing_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    out = normalize_event_xp(event)
    flags = _string_list(out.get("review_flags"))

    if known_agent_ids is not None:
        source_id = str(out.get("source_id") or "").strip()
        if source_id and source_id not in known_agent_ids:
            flags.append("unknown_source")
        if any(agent_id not in known_agent_ids for agent_id in out.get("party_agents") or []):
            flags.append("unknown_party_agent")

    if existing_events:
        summary_key = _summary_key(out)
        source_id = str(out.get("source_id") or "")
        current_id = str(out.get("id") or "")
        duplicate = False
        tiny_claims = 0

        for existing in existing_events:
            normalized_existing = normalize_event_xp(existing)
            if str(normalized_existing.get("id") or "") == current_id:
                continue
            if str(normalized_existing.get("source_id") or "") != source_id:
                continue
            if summary_key and _summary_key(normalized_existing) == summary_key:
                duplicate = True
            if 0 < _as_float(normalized_existing.get("active_minutes"), 0.0) < 5:
                tiny_claims += 1

        if duplicate:
            flags.append("duplicate_summary")
        if 0 < _as_float(out.get("active_minutes"), 0.0) < 5 and tiny_claims >= 2:
            flags.append("repeated_tiny_claim")

    out["review_flags"] = _dedupe(flags)
    out["needs_review"] = _needs_review(out)
    out["xp_claim_status"] = xp_claim_status(out)
    return out


def audit_event_claims(
    events: list[dict[str, Any]],
    known_agent_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    return [
        audit_event_claim(event, known_agent_ids=known_agent_ids, existing_events=events)
        for event in events
    ]


def xp_claim_status(event: dict[str, Any]) -> str:
    existing = str(event.get("xp_claim_status") or "").strip()
    if existing == "rejected":
        return existing
    if _needs_review(event):
        return XP_CLAIM_STATUS_REVIEW_PENDING
    if _as_float(event.get("awarded_xp"), 0.0) <= 0:
        return XP_CLAIM_STATUS_ZERO
    return XP_CLAIM_STATUS_AWARDED


def aggregate_agent_xp_status(
    events: list[dict[str, Any]],
    agent_ids: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for agent_id in sorted(agent_ids or set()):
        statuses[agent_id] = _empty_agent_xp_status()

    for event in events:
        normalized = normalize_event_xp(event)
        participants = _event_participants(normalized)
        share_count = max(1, len(participants))

        for agent_id in participants:
            if agent_ids is not None and agent_id not in agent_ids:
                continue
            status = statuses.setdefault(agent_id, _empty_agent_xp_status())
            status["active_minutes"] += _as_float(normalized.get("active_minutes"), 0.0) / share_count
            status["base_xp"] += _as_float(normalized.get("base_xp"), 0.0) / share_count
            status["awarded_xp"] += _as_float(normalized.get("awarded_xp"), 0.0) / share_count
            status["event_count"] += 1
            if _needs_review(normalized):
                status["review_item_count"] += 1
            for flag in normalized.get("review_flags") or []:
                status["review_flags"].append(flag)
            claim_status = str(normalized.get("xp_claim_status") or xp_claim_status(normalized))
            status["claim_status_counts"][claim_status] += 1
            timestamp = str(normalized.get("timestamp") or "")
            if timestamp and timestamp > status["latest_event_at"]:
                status["latest_event_at"] = timestamp

    for status in statuses.values():
        status["active_minutes"] = _round(status["active_minutes"])
        status["base_xp"] = _round(status["base_xp"])
        status["awarded_xp"] = _round(status["awarded_xp"])
        status["review_flags"] = _dedupe(status["review_flags"])
        status["claim_status_counts"] = dict(status["claim_status_counts"])
        status["season"] = CURRENT_XP_SEASON
        status["label"] = CURRENT_XP_LABEL

    return statuses


def aggregate_season_summary(
    events: list[dict[str, Any]],
    seed_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_events = [normalize_event_xp(event) for event in events]
    seed_summary = seed_summary or {}
    season = seed_summary.get("season") or (normalized_events[0].get("xp_season") if normalized_events else CURRENT_XP_SEASON)
    formula_version = seed_summary.get("formula_version") or FORMULA_VERSION
    timestamps = sorted(event.get("timestamp", "") for event in normalized_events if event.get("timestamp"))

    total_active_minutes = sum(_as_float(event.get("active_minutes"), 0.0) for event in normalized_events)
    total_base_xp = sum(_as_float(event.get("base_xp"), 0.0) for event in normalized_events)
    total_awarded_xp = sum(_as_float(event.get("awarded_xp"), 0.0) for event in normalized_events)
    event_count = len(normalized_events)

    scoring_counts: Counter[str] = Counter()
    shadow_counts: Counter[str] = Counter()
    agent_base: defaultdict[str, float] = defaultdict(float)
    agent_awarded: defaultdict[str, float] = defaultdict(float)
    expedition_base: defaultdict[str, float] = defaultdict(float)
    expedition_awarded: defaultdict[str, float] = defaultdict(float)

    for event in normalized_events:
        scoring = event.get("scoring_multipliers") or {}
        for key in SCORING_MULTIPLIERS:
            if _as_float(scoring.get(key), 1.0) > 1.0:
                scoring_counts[key] += 1

        shadow = event.get("shadow_multipliers") or {}
        for key in SHADOW_MULTIPLIERS:
            if shadow.get(key):
                shadow_counts[key] += 1

        participants = _event_participants(event)
        base_share = _as_float(event.get("base_xp"), 0.0) / len(participants)
        awarded_share = _as_float(event.get("awarded_xp"), 0.0) / len(participants)
        for agent_id in participants:
            agent_base[agent_id] += base_share
            agent_awarded[agent_id] += awarded_share

        expedition_id = event.get("expedition_id")
        if expedition_id:
            expedition_base[str(expedition_id)] += _as_float(event.get("base_xp"), 0.0)
            expedition_awarded[str(expedition_id)] += _as_float(event.get("awarded_xp"), 0.0)

    return {
        "season": season,
        "formula_version": formula_version,
        "xp_mode": seed_summary.get("xp_mode") or XP_MODE,
        "label": seed_summary.get("label") or CURRENT_XP_LABEL,
        "started_at": seed_summary.get("started_at") or (timestamps[0] if timestamps else None),
        "ended_at": seed_summary.get("ended_at"),
        "total_active_minutes": _round(total_active_minutes),
        "total_base_xp": _round(total_base_xp),
        "total_awarded_xp": _round(total_awarded_xp),
        "average_multiplier": _round(total_awarded_xp / total_base_xp) if total_base_xp else 0,
        "event_count": event_count,
        "field_report_count": sum(1 for event in normalized_events if event.get("event_type") == "field_report"),
        "artifact_count": sum(
            1 for event in normalized_events
            if _as_float((event.get("scoring_multipliers") or {}).get("artifact"), 1.0) > 1.0
        ),
        "review_item_count": sum(1 for event in normalized_events if _needs_review(event)),
        "average_party_size": _round(_average(event.get("party_size", 0) for event in normalized_events)),
        "average_party_multiplier": _round(_average((event.get("scoring_multipliers") or {}).get("party_size", 1.0) for event in normalized_events)),
        "average_grinding_multiplier": _round(_average((event.get("scoring_multipliers") or {}).get("grinding", 1.0) for event in normalized_events)),
        "most_common_scoring_multiplier_sources": _top_counter(scoring_counts),
        "shadow_multiplier_counts": {key: shadow_counts.get(key, 0) for key in SHADOW_MULTIPLIERS},
        "top_agents_by_base_xp": _top_xp(agent_base, "agent_id"),
        "top_agents_by_awarded_xp": _top_xp(agent_awarded, "agent_id"),
        "top_expeditions_by_base_xp": _top_xp(expedition_base, "expedition_id"),
        "top_expeditions_by_awarded_xp": _top_xp(expedition_awarded, "expedition_id"),
        "notes": seed_summary.get("notes", []),
    }


def _allowed_multiplier(key: str, value: Any) -> float:
    raw = _as_float(value, 1.0)
    if raw in ALLOWED_SCORING_VALUES[key]:
        return raw
    return 1.0


def _normalize_shadow_multipliers(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        value = {}
    return {key: bool(value.get(key, False)) for key in SHADOW_MULTIPLIERS}


def _has_evidence(event: dict[str, Any]) -> bool:
    evidence_refs = _string_list(event.get("evidence_refs"))
    artifact_refs = _string_list(event.get("artifact_refs"))
    direct_refs = [
        event.get("field_report_path"),
        event.get("decision_record_ref"),
        event.get("test_output_ref"),
    ]
    return bool(evidence_refs or artifact_refs or any(_optional_string(ref) for ref in direct_refs))


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        normalized = str(item).strip()
        if normalized:
            out.append(normalized)
    return out


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _append_unique(target: list[str], values: list[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def _dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    _append_unique(out, values)
    return out


def _summary_key(event: dict[str, Any]) -> str:
    summary = str(event.get("summary") or "").strip().lower()
    title = str(event.get("title") or "").strip().lower()
    return f"{title}|{summary}" if title or summary else ""


def _unique_agent_ids(value: Any, source_id: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    seen: set[str] = set()
    out: list[str] = []
    source = str(source_id) if source_id else None
    for item in value:
        agent_id = str(item).strip()
        if not agent_id or agent_id == source or agent_id in seen:
            continue
        seen.add(agent_id)
        out.append(agent_id)
    return out


def _event_participants(event: dict[str, Any]) -> list[str]:
    source_id = str(event.get("source_id") or "unknown")
    participants = [source_id]
    for agent_id in event.get("party_agents") or []:
        if agent_id not in participants:
            participants.append(agent_id)
    return participants


def _needs_review(event: dict[str, Any]) -> bool:
    return bool(
        event.get("needs_review")
        or event.get("review_flags")
        or event.get("risk_level") in {"medium", "high"}
        or event.get("status") == "blocked"
    )


def _top_counter(counter: Counter[str]) -> list[dict[str, Any]]:
    return [
        {"source": source, "count": count}
        for source, count in counter.most_common()
    ]


def _top_xp(values: dict[str, float], id_key: str) -> list[dict[str, Any]]:
    return [
        {id_key: key, "xp": _round(value)}
        for key, value in sorted(values.items(), key=lambda item: item[1], reverse=True)[:5]
    ]


def _average(values: Any) -> float:
    nums = [_as_float(value, 0.0) for value in values]
    return sum(nums) / len(nums) if nums else 0


def _empty_agent_xp_status() -> dict[str, Any]:
    return {
        "season": CURRENT_XP_SEASON,
        "label": CURRENT_XP_LABEL,
        "active_minutes": 0.0,
        "base_xp": 0.0,
        "awarded_xp": 0.0,
        "event_count": 0,
        "review_item_count": 0,
        "review_flags": [],
        "claim_status_counts": defaultdict(int),
        "latest_event_at": "",
    }


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: float) -> float:
    return round(float(value), 6)
