from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .season import current_xp_season, event_in_window
from .xp import FORMULA_VERSION

PROPOSAL_VOTES = {"support", "oppose", "abstain"}
REQUIRED_ABSTAIN_RESPONSE_KIND = "required_abstain"
RECORDED_RESPONSE_KIND = "recorded"
AMENDED_AFTER_PROMPT_RESPONSE_KIND = "amended_after_prompt"
PROPOSAL_RESPONSE_KINDS = {
    RECORDED_RESPONSE_KIND,
    REQUIRED_ABSTAIN_RESPONSE_KIND,
    AMENDED_AFTER_PROMPT_RESPONSE_KIND,
}
PEER_REVIEW_XP_STATUSES = {"pending_outcome", "useful", "not_useful", "not_awarded"}
PEER_REVIEW_XP_MAX_PER_ASSESSMENT = 0.25
LATE_PARTICIPATION_XP_MULTIPLIER = 0.5
LATE_PARTICIPATION_PENALTY_REASON = (
    "50% late-participation penalty: the specialist waited for an amendment request "
    "instead of replying when the proposal was first available."
)
LATE_PARTICIPATION_MEMORY_NOTE = (
    "Remember this next time: proactive proposal review can earn full peer-review XP; "
    "waiting for a nudge caps this review at half credit."
)
DEFAULT_WORK_QUEUE_NOTE = (
    "Actual work phase: use Implement Proposal to authorize a proposal-scoped OpenClaw route."
)
LEGACY_WORK_QUEUE_NOTES = {
    "Moved into the local work queue. No implementation automation is launched.",
    (
        "Queued for actual implementation. Next step: open a separate local work session from this proposal; "
        "no implementation automation is launched."
    ),
}
PROPOSAL_STATUSES = {
    "draft",
    "pending",
    "approved",
    "in_progress",
    "implementation_requested",
    "denied",
    "revise_requested",
    "deferred",
    "implemented",
    "accepted",
    "rejected",
    "archived",
}
WORK_START_ELIGIBLE_STATUSES = {"approved"}
IMPLEMENTATION_REQUEST_ELIGIBLE_STATUSES = {"in_progress"}
IMPLEMENTATION_COMPLETE_ELIGIBLE_STATUSES = {"implementation_requested"}
IMPLEMENTATION_REVIEW_ELIGIBLE_STATUSES = {"implemented"}
IMPLEMENTATION_REVIEW_DECISIONS = {"accept", "reject"}
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
DEFAULT_DECISION_NOTES = {
    "approve": "Approved for planning. No implementation triggered.",
    "deny": "Denied during Season 0.x testing. No implementation triggered.",
    "revise": "Revision requested during Season 0.x testing. Agent should ask follow-up questions before resubmitting.",
    "defer": "Deferred during Season 0.x testing. No implementation triggered.",
}
CLARIFICATION_QUESTIONS = [
    "What did you not like about this proposal?",
    "Was the issue scope, timing, risk, aesthetics, usefulness, or wording?",
    "Would you prefer option A or option B?",
    "Should this be smaller and safer, or more ambitious?",
    "What would make this proposal acceptable?",
    "Should this become a later milestone instead of an immediate task?",
]
DEFAULT_IMPLEMENTATION_REQUEST_NOTE = (
    "Implementation authorized for proposal-scoped OpenClaw routing. "
    "Expedition HQ records the route, provider choices, skips, evidence, and outcome."
)
DEFAULT_IMPLEMENTATION_COMPLETE_NOTE = (
    "Implementation has been reported complete and is waiting for August's final review."
)
DEFAULT_IMPLEMENTATION_ACCEPT_NOTE = (
    "Accepted after final review. The proposal is complete."
)
DEFAULT_IMPLEMENTATION_REJECT_NOTE = (
    "Rejected after final review. The implementation did not satisfy the proposal yet."
)
PROVIDER_ROLES = [
    "implementer",
    "critic",
    "research_crosscheck",
    "source_checker",
    "cheap_reasoning_check",
    "final_synthesizer",
]
DEFAULT_SELECTED_ROUTE_AGENTS = [
    {
        "agent_id": "openclaw-main",
        "provider": "OpenClaw",
        "access_mode": "local_gateway",
        "trust_level": "trusted_implementer",
        "task_role": "final_synthesizer",
        "route_status": "selected",
        "cost_quota_notes": "Route owner; choose available agents and keep a compact implementation record.",
        "reason": "OpenClaw owns provider routing while Expedition HQ observes the outcome.",
    },
    {
        "agent_id": "home-windows-codex",
        "provider": "Codex local",
        "access_mode": "local_repo",
        "trust_level": "trusted_implementer",
        "task_role": "implementer",
        "route_status": "selected",
        "cost_quota_notes": "Reserve local Codex work for repo edits, tests, private context, and final validation.",
        "reason": "Trusted local implementation should handle repo changes and evidence collection.",
    },
    {
        "agent_id": "codex-memory-operator",
        "provider": "Codex local",
        "access_mode": "local_review",
        "trust_level": "trusted_reviewer",
        "task_role": "critic",
        "route_status": "selected",
        "cost_quota_notes": "Use for local review and memory-policy-sensitive critique, not automatic durable-memory writes.",
        "reason": "Reviewers help keep Completed tied to accepted evidence, not merely changed files.",
    },
]
DEFAULT_CANDIDATE_PROVIDERS = [
    {
        "agent_id": "copilot-visiting-specialist",
        "provider": "Copilot",
        "access_mode": "free_or_manual_relay",
        "trust_level": "unprofiled_candidate",
        "task_role": "cheap_reasoning_check",
        "route_status": "skipped",
        "unavailable_reason": "Candidate is not profiled or attached to an enabled OpenClaw route yet.",
        "cost_quota_notes": "Use for cheap alternate reasoning after profiling; do not treat as trusted implementation evidence.",
    },
    {
        "agent_id": "claude-visiting-specialist",
        "provider": "Claude",
        "access_mode": "free_or_manual_relay",
        "trust_level": "unprofiled_candidate",
        "task_role": "critic",
        "route_status": "skipped",
        "unavailable_reason": "Candidate is not profiled or attached to an enabled OpenClaw route yet.",
        "cost_quota_notes": "Use for careful critique when privacy and quota allow.",
    },
    {
        "agent_id": "perplexity-visiting-specialist",
        "provider": "Perplexity",
        "access_mode": "free_or_manual_relay",
        "trust_level": "unprofiled_candidate",
        "task_role": "source_checker",
        "route_status": "skipped",
        "unavailable_reason": "Candidate is not profiled or attached to an enabled OpenClaw route yet.",
        "cost_quota_notes": "Use for source-aware scouting when current references are needed.",
    },
    {
        "agent_id": "gemini-visiting-specialist",
        "provider": "Gemini",
        "access_mode": "free_or_manual_relay",
        "trust_level": "unprofiled_candidate",
        "task_role": "research_crosscheck",
        "route_status": "skipped",
        "unavailable_reason": "Candidate is not profiled or attached to an enabled OpenClaw route yet.",
        "cost_quota_notes": "Use for broad alternate context after capability profiling.",
    },
    {
        "agent_id": "deepseek-visiting-specialist",
        "provider": "DeepSeek",
        "access_mode": "free_or_manual_relay",
        "trust_level": "unprofiled_candidate",
        "task_role": "cheap_reasoning_check",
        "route_status": "skipped",
        "unavailable_reason": "Candidate is not profiled or attached to an enabled OpenClaw route yet.",
        "cost_quota_notes": "Use for low-cost reasoning checks after safe profiling.",
    },
    {
        "agent_id": "kimi-visiting-specialist",
        "provider": "Kimi",
        "access_mode": "free_or_manual_relay",
        "trust_level": "unprofiled_candidate",
        "task_role": "research_crosscheck",
        "route_status": "skipped",
        "unavailable_reason": "Candidate is not profiled or attached to an enabled OpenClaw route yet.",
        "cost_quota_notes": "Use for long-context review after safe profiling.",
    },
    {
        "agent_id": "manus-visiting-specialist",
        "provider": "Manus",
        "access_mode": "free_or_manual_relay",
        "trust_level": "unprofiled_candidate",
        "task_role": "critic",
        "route_status": "skipped",
        "unavailable_reason": "Candidate is not profiled or attached to an enabled OpenClaw route yet.",
        "cost_quota_notes": "Use only after execution boundaries are proven safe.",
    },
]


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

    out["xp_season"] = out.get("xp_season") or current_xp_season()
    out["formula_version"] = out.get("formula_version") or FORMULA_VERSION
    out["proposal_type"] = proposal_type
    out["created_at"] = out.get("created_at") or now
    out["estimated_active_minutes"] = _non_negative(out.get("estimated_active_minutes"), 0.0)
    out["requested_xp_wager"] = requested_wager
    out["confidence"] = min(max(_non_negative(out.get("confidence"), 0.0), 0.0), 1.0)
    out["risk_level"] = out.get("risk_level") or "low"
    out["affected_areas"] = _string_list(out.get("affected_areas"))
    out["acceptance_criteria"] = _string_list(out.get("acceptance_criteria"))
    out["rollback_plan"] = out.get("rollback_plan") or ""
    out["status"] = status
    out["broadcast_status"] = out.get("broadcast_status") or ("broadcasted" if status != "draft" else "draft")
    out["broadcasted_at"] = out.get("broadcasted_at") or (out.get("created_at") if status != "draft" else None)
    out["eligible_agent_ids"] = _string_list(out.get("eligible_agent_ids"))
    out["council_votes"] = complete_required_council_votes(
        _proposal_votes(out.get("council_votes"), out.get("proposal_id", "")),
        out["eligible_agent_ids"],
        out.get("proposal_id", ""),
        out.get("broadcasted_at") or out["created_at"],
        require_responses=out["broadcast_status"] != "draft",
    )
    out["council_summary"] = proposal_council_summary(out["council_votes"], len(out["eligible_agent_ids"]))
    out["decision"] = out.get("decision")
    out["decision_note"] = out.get("decision_note")
    out["decision_note_provided"] = bool(out.get("decision_note_provided", bool(out.get("decision_note"))))
    out["decided_at"] = out.get("decided_at")
    raw_work_start_note = out.get("work_start_note")
    work_start_note = normalize_work_start_note(raw_work_start_note)
    work_start_note_is_default = str(raw_work_start_note or "").strip() in LEGACY_WORK_QUEUE_NOTES or (
        work_start_note == DEFAULT_WORK_QUEUE_NOTE
    )
    out["work_started_at"] = out.get("work_started_at")
    out["work_start_note"] = work_start_note
    out["work_start_note_provided"] = bool(
        out.get("work_start_note_provided", bool(work_start_note and not work_start_note_is_default))
    )
    out["implementation_session_id"] = str(out.get("implementation_session_id") or "").strip() or None
    out["implementation_requested_at"] = out.get("implementation_requested_at")
    out["implementation_request_note"] = str(out.get("implementation_request_note") or "").strip() or None
    out["implementation_request_note_provided"] = bool(
        out.get("implementation_request_note_provided", bool(out.get("implementation_request_note")))
    )
    out["implementation_brief_path"] = str(out.get("implementation_brief_path") or "").strip() or None
    out["implementation_dispatch_status"] = (
        str(out.get("implementation_dispatch_status") or "").strip() or None
    )
    out["implementation_route_plan"] = normalize_implementation_route_plan(out.get("implementation_route_plan"))
    out["implementation_completed_at"] = out.get("implementation_completed_at")
    out["implementation_completion_note"] = str(out.get("implementation_completion_note") or "").strip() or None
    out["implementation_evidence_refs"] = _string_list(out.get("implementation_evidence_refs"))
    out["implementation_reviewed_at"] = out.get("implementation_reviewed_at")
    out["implementation_review_note"] = str(out.get("implementation_review_note") or "").strip() or None
    out["implementation_reviewer_id"] = str(out.get("implementation_reviewer_id") or "").strip() or None
    out["simulated_xp_gain"] = simulated_gain
    out["simulated_xp_loss"] = simulated_loss
    out["dialogue_messages"] = _dialogue_messages(out.get("dialogue_messages"))
    out["updated_at"] = out.get("updated_at") or out["created_at"]
    if out["status"] != "draft" and not out.get("broadcasted_at"):
        out["broadcasted_at"] = out["created_at"]
    return out


def normalize_vote(vote: dict[str, Any], proposal_id: str) -> dict[str, Any]:
    out = dict(vote)
    agent_id = str(out.get("agent_id") or "").strip()
    vote_value = str(out.get("vote") or "abstain").strip()
    if vote_value not in PROPOSAL_VOTES:
        vote_value = "abstain"

    confidence = min(max(_non_negative(out.get("confidence"), 0.0), 0.0), 1.0)
    response_kind = str(out.get("response_kind") or RECORDED_RESPONSE_KIND).strip() or RECORDED_RESPONSE_KIND
    if response_kind not in PROPOSAL_RESPONSE_KINDS:
        response_kind = RECORDED_RESPONSE_KIND
    peer_review_xp_multiplier = _peer_review_xp_multiplier(response_kind, out.get("peer_review_xp_multiplier"))
    peer_review_xp_cap = PEER_REVIEW_XP_MAX_PER_ASSESSMENT * peer_review_xp_multiplier
    peer_review_xp = min(_non_negative(out.get("peer_review_xp"), 0.0), peer_review_xp_cap)
    usefulness_status = str(out.get("usefulness_status") or "pending_outcome").strip()
    if usefulness_status not in PEER_REVIEW_XP_STATUSES:
        usefulness_status = "pending_outcome"
    if usefulness_status != "useful":
        peer_review_xp = 0.0

    created_at = str(out.get("created_at") or _now()).strip()
    safe_proposal_id = str(out.get("proposal_id") or proposal_id).strip()
    vote_id = str(out.get("vote_id") or f"vote-{safe_proposal_id}-{agent_id}").strip()

    return {
        "vote_id": vote_id,
        "proposal_id": safe_proposal_id,
        "agent_id": agent_id,
        "vote": vote_value,
        "confidence": confidence,
        "reasoning": _required_string(out.get("reasoning"), "No reasoning recorded."),
        "expected_benefit": _required_string(out.get("expected_benefit"), "No expected benefit recorded."),
        "expected_failure_mode": _required_string(out.get("expected_failure_mode"), "No expected failure mode recorded."),
        "risk_notes": _required_string(out.get("risk_notes"), "No risk notes recorded."),
        "context_notes": str(out.get("context_notes") or "").strip(),
        "created_at": created_at,
        "usefulness_status": usefulness_status,
        "peer_review_xp": peer_review_xp,
        "response_kind": response_kind,
        "peer_review_xp_multiplier": peer_review_xp_multiplier,
        "peer_review_xp_penalty_reason": str(out.get("peer_review_xp_penalty_reason") or "").strip(),
        "agent_memory_note": str(out.get("agent_memory_note") or "").strip(),
    }


def apply_vote(proposal: dict[str, Any], vote: dict[str, Any]) -> dict[str, Any]:
    out = normalize_proposal(proposal)
    incoming = normalize_vote(vote, out["proposal_id"])
    agent_id = incoming["agent_id"]
    if not agent_id:
        raise ValueError("Vote requires agent_id.")
    if agent_id not in out.get("eligible_agent_ids", []):
        raise ValueError(f"Agent is not eligible to review this proposal: {agent_id}")

    existing_for_agent = next(
        (existing for existing in out.get("council_votes", []) if existing.get("agent_id") == agent_id),
        None,
    )
    if existing_for_agent and existing_for_agent.get("response_kind") == REQUIRED_ABSTAIN_RESPONSE_KIND:
        incoming = apply_late_participation_penalty(incoming)

    votes = [existing for existing in out.get("council_votes", []) if existing.get("agent_id") != agent_id]
    votes.append(incoming)
    out["council_votes"] = sorted(votes, key=lambda item: (item.get("created_at", ""), item.get("agent_id", "")))
    out["council_votes"] = complete_required_council_votes(
        out["council_votes"],
        out.get("eligible_agent_ids", []),
        out["proposal_id"],
        out.get("broadcasted_at") or out.get("created_at") or _now(),
        require_responses=out.get("broadcast_status") != "draft",
    )
    out["council_summary"] = proposal_council_summary(out["council_votes"], len(out.get("eligible_agent_ids", [])))
    out["updated_at"] = _now()
    if out.get("status") != "draft" and not out.get("broadcasted_at"):
        out["broadcasted_at"] = out["created_at"]
    return out


def proposal_council_summary(votes: list[dict[str, Any]], eligible_count: int) -> dict[str, Any]:
    counts = {vote: 0 for vote in sorted(PROPOSAL_VOTES)}
    confidence_totals = {vote: 0.0 for vote in sorted(PROPOSAL_VOTES)}
    confidence_counts = {vote: 0 for vote in sorted(PROPOSAL_VOTES)}
    peer_review_xp_awarded = 0.0
    useful_count = 0
    pending_count = 0
    amendment_requested_count = 0

    for vote in votes:
        vote_value = str(vote.get("vote") or "abstain")
        if vote_value not in PROPOSAL_VOTES:
            vote_value = "abstain"
        is_required_abstain = vote.get("response_kind") == REQUIRED_ABSTAIN_RESPONSE_KIND
        if is_required_abstain:
            amendment_requested_count += 1
        counts[vote_value] += 1
        confidence_totals[vote_value] += _non_negative(vote.get("confidence"), 0.0)
        confidence_counts[vote_value] += 1
        peer_review_xp_awarded += _non_negative(vote.get("peer_review_xp"), 0.0)
        if vote.get("usefulness_status") == "useful" and not is_required_abstain:
            useful_count += 1
        if vote.get("usefulness_status") == "pending_outcome" and not is_required_abstain:
            pending_count += 1

    confidence_by_vote = {
        vote: round(confidence_totals[vote] / confidence_counts[vote], 4) if confidence_counts[vote] else 0.0
        for vote in sorted(PROPOSAL_VOTES)
    }
    participation_count = len({str(vote.get("agent_id") or "") for vote in votes if vote.get("agent_id")})
    peer_review_participation_count = participation_count - amendment_requested_count
    abstain_count = counts["abstain"]
    return {
        "eligible_count": eligible_count,
        "participation_count": participation_count,
        "participation_rate": round(participation_count / eligible_count, 4) if eligible_count else 0.0,
        "peer_review_participation_count": peer_review_participation_count,
        "peer_review_participation_rate": round(peer_review_participation_count / eligible_count, 4) if eligible_count else 0.0,
        "amendment_requested_count": amendment_requested_count,
        "vote_counts": counts,
        "average_confidence_by_vote": confidence_by_vote,
        "healthy_abstain_count": abstain_count,
        "peer_review_xp_awarded": round(peer_review_xp_awarded, 6),
        "useful_assessment_count": useful_count,
        "pending_assessment_count": pending_count,
        "guidance": "Default abstains are amendment requests: specialists should support, oppose, or write a useful abstain reason to earn peer-review XP.",
    }


def complete_required_council_votes(
    votes: list[dict[str, Any]],
    eligible_agent_ids: list[str],
    proposal_id: str,
    created_at: str,
    *,
    require_responses: bool,
) -> list[dict[str, Any]]:
    if not require_responses:
        return sorted(votes, key=lambda item: (item.get("created_at", ""), item.get("agent_id", "")))

    completed = list(votes)
    seen_agents = {str(vote.get("agent_id") or "").strip() for vote in votes if vote.get("agent_id")}
    for agent_id in eligible_agent_ids:
        if agent_id in seen_agents:
            continue
        completed.append(required_abstain_vote(proposal_id, agent_id, created_at))
        seen_agents.add(agent_id)
    return sorted(completed, key=lambda item: (item.get("created_at", ""), item.get("agent_id", "")))


def required_abstain_vote(proposal_id: str, agent_id: str, created_at: str) -> dict[str, Any]:
    return {
        "vote_id": f"vote-{proposal_id}-{agent_id}-required-abstain",
        "proposal_id": proposal_id,
        "agent_id": agent_id,
        "vote": "abstain",
        "confidence": 0.0,
        "reasoning": "Abstain - amendment requested. This specialist has not supplied useful peer-review reasoning yet.",
        "expected_benefit": "Amending to support, oppose, or a useful abstain reason can earn peer-review XP and make the proposal record more trustworthy.",
        "expected_failure_mode": "Leaving this placeholder unchanged adds no judgment and earns no peer-review XP.",
        "risk_notes": "Do not award peer-review XP until the specialist records a substantive reason.",
        "context_notes": "Peer-review XP rewards useful participation; this placeholder asks the specialist to amend the response.",
        "created_at": created_at,
        "usefulness_status": "not_awarded",
        "peer_review_xp": 0.0,
        "peer_review_xp_multiplier": 0.0,
        "peer_review_xp_penalty_reason": "",
        "agent_memory_note": LATE_PARTICIPATION_MEMORY_NOTE,
        "response_kind": REQUIRED_ABSTAIN_RESPONSE_KIND,
    }


def apply_late_participation_penalty(vote: dict[str, Any]) -> dict[str, Any]:
    out = dict(vote)
    out["response_kind"] = AMENDED_AFTER_PROMPT_RESPONSE_KIND
    out["peer_review_xp_multiplier"] = LATE_PARTICIPATION_XP_MULTIPLIER
    out["peer_review_xp"] = min(
        _non_negative(out.get("peer_review_xp"), 0.0),
        PEER_REVIEW_XP_MAX_PER_ASSESSMENT * LATE_PARTICIPATION_XP_MULTIPLIER,
    )
    out["peer_review_xp_penalty_reason"] = LATE_PARTICIPATION_PENALTY_REASON
    out["agent_memory_note"] = LATE_PARTICIPATION_MEMORY_NOTE
    out["context_notes"] = _append_note(out.get("context_notes"), LATE_PARTICIPATION_PENALTY_REASON)
    out["context_notes"] = _append_note(out.get("context_notes"), LATE_PARTICIPATION_MEMORY_NOTE)
    return out


def aggregate_peer_review_status(
    proposals: list[dict[str, Any]],
    agent_ids: set[str] | None = None,
    season_window: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for agent_id in sorted(agent_ids or set()):
        statuses[agent_id] = _empty_peer_review_status(season_window)

    for proposal in proposals:
        normalized = normalize_proposal(proposal)
        for vote in normalized.get("council_votes", []):
            agent_id = str(vote.get("agent_id") or "").strip()
            if not agent_id or (agent_ids is not None and agent_id not in agent_ids):
                continue
            status = statuses.setdefault(agent_id, _empty_peer_review_status(season_window))
            _add_peer_review_vote(status["peer_review_all_time"], vote)
            if season_window is None or _vote_in_season_window(vote, normalized, season_window):
                _add_peer_review_vote(status, vote)

    for status in statuses.values():
        status["peer_review_xp"] = round(status["peer_review_xp"], 6)
        status["peer_review_all_time"]["peer_review_xp"] = round(status["peer_review_all_time"]["peer_review_xp"], 6)
    return statuses


def apply_decision(proposal: dict[str, Any], decision: str, decision_note: str | None) -> dict[str, Any]:
    out = normalize_proposal(proposal)
    status = DECISION_TO_STATUS[decision]
    requested_wager = _non_negative(out.get("requested_xp_wager"), 0.0)
    note_provided = bool(str(decision_note or "").strip())
    note = str(decision_note or "").strip() or DEFAULT_DECISION_NOTES[decision]
    decided_at = _now()
    out["status"] = status
    out["decision"] = decision
    out["decision_note"] = note
    out["decision_note_provided"] = note_provided
    out["decided_at"] = decided_at
    out["updated_at"] = out["decided_at"]
    out["simulated_xp_gain"] = 0.0
    out["simulated_xp_loss"] = requested_wager if decision == "deny" else 0.0
    out["dialogue_messages"] = _decision_dialogue_messages(out, decision, note, note_provided, decided_at)
    return out


def apply_work_start(proposal: dict[str, Any], start_note: str | None) -> dict[str, Any]:
    out = normalize_proposal(proposal)
    if out.get("status") == "in_progress" and out.get("work_started_at"):
        return out
    if out.get("status") not in WORK_START_ELIGIBLE_STATUSES:
        raise ValueError("Only approved, not-yet-started proposals can be moved into local work.")

    note_provided = bool(str(start_note or "").strip())
    note = normalize_work_start_note(start_note) or DEFAULT_WORK_QUEUE_NOTE
    started_at = _now()
    out["status"] = "in_progress"
    out["work_started_at"] = started_at
    out["work_start_note"] = note
    out["work_start_note_provided"] = note_provided
    out["updated_at"] = started_at
    out["dialogue_messages"] = _work_start_dialogue_messages(out, note, note_provided, started_at)
    return out


def apply_implementation_request(
    proposal: dict[str, Any],
    request_note: str | None,
    brief_path: str | None = None,
) -> dict[str, Any]:
    out = normalize_proposal(proposal)
    if out.get("status") == "implementation_requested" and out.get("implementation_requested_at"):
        return out
    if out.get("status") not in IMPLEMENTATION_REQUEST_ELIGIBLE_STATUSES:
        raise ValueError("Only queued proposals can request implementation.")

    note_provided = bool(str(request_note or "").strip())
    note = str(request_note or "").strip() or DEFAULT_IMPLEMENTATION_REQUEST_NOTE
    requested_at = _now()
    out["status"] = "implementation_requested"
    out["implementation_requested_at"] = requested_at
    out["implementation_request_note"] = note
    out["implementation_request_note_provided"] = note_provided
    out["implementation_session_id"] = out.get("implementation_session_id") or _implementation_session_id(
        out["proposal_id"],
        requested_at,
    )
    out["implementation_brief_path"] = brief_path or out.get("implementation_brief_path")
    out["implementation_dispatch_status"] = "queued"
    out["implementation_route_plan"] = implementation_route_plan(out)
    out["updated_at"] = requested_at
    out["dialogue_messages"] = _implementation_dialogue_messages(
        out,
        note,
        note_provided,
        requested_at,
        "implementation_request",
        "implementation-request",
    )
    return out


def apply_implementation_complete(
    proposal: dict[str, Any],
    completion_note: str | None,
    evidence_refs: list[str] | None,
) -> dict[str, Any]:
    out = normalize_proposal(proposal)
    if out.get("status") not in IMPLEMENTATION_COMPLETE_ELIGIBLE_STATUSES:
        raise ValueError("Only implementation-requested proposals can be marked implemented.")

    note_provided = bool(str(completion_note or "").strip())
    note = str(completion_note or "").strip() or DEFAULT_IMPLEMENTATION_COMPLETE_NOTE
    completed_at = _now()
    out["status"] = "implemented"
    out["implementation_completed_at"] = completed_at
    out["implementation_completion_note"] = note
    out["implementation_evidence_refs"] = _string_list(evidence_refs)
    out["updated_at"] = completed_at
    out["dialogue_messages"] = _implementation_dialogue_messages(
        out,
        note,
        note_provided,
        completed_at,
        "implementation_complete",
        "implementation-complete",
    )
    return out


def apply_implementation_review(
    proposal: dict[str, Any],
    review_decision: str,
    review_note: str | None,
    reviewer_id: str | None,
) -> dict[str, Any]:
    out = normalize_proposal(proposal)
    if out.get("status") not in IMPLEMENTATION_REVIEW_ELIGIBLE_STATUSES:
        raise ValueError("Only implemented proposals can receive final review.")
    if review_decision not in IMPLEMENTATION_REVIEW_DECISIONS:
        raise ValueError("Implementation review must be accept or reject.")

    reviewer = str(reviewer_id or "").strip() or "august"
    note_provided = bool(str(review_note or "").strip())
    note = str(review_note or "").strip() or (
        DEFAULT_IMPLEMENTATION_ACCEPT_NOTE if review_decision == "accept" else DEFAULT_IMPLEMENTATION_REJECT_NOTE
    )
    reviewed_at = _now()
    out["status"] = "accepted" if review_decision == "accept" else "rejected"
    out["implementation_reviewed_at"] = reviewed_at
    out["implementation_review_note"] = note
    out["implementation_reviewer_id"] = reviewer
    out["updated_at"] = reviewed_at
    out["simulated_xp_gain"] = out["requested_xp_wager"] if review_decision == "accept" else 0.0
    out["simulated_xp_loss"] = 0.0
    out["dialogue_messages"] = _implementation_dialogue_messages(
        out,
        note,
        note_provided,
        reviewed_at,
        "implementation_review",
        f"implementation-review-{review_decision}",
        author_id=reviewer,
    )
    return out


def proposal_decision_event(proposal: dict[str, Any]) -> dict[str, Any]:
    decision = proposal.get("decision") or "unknown"
    wager = _non_negative(proposal.get("requested_xp_wager"), 0.0)
    loss = _non_negative(proposal.get("simulated_xp_loss"), 0.0)
    effect = f"simulated loss {loss:g} XP" if loss else "no simulated XP loss"
    timestamp = proposal.get("decided_at") or _now()
    note = proposal.get("decision_note") or ""
    event_type = "proposal_revision_requested" if decision == "revise" else "proposal_decision"
    return {
        "id": f"evt-proposal-{proposal['proposal_id']}-{decision}-{timestamp.replace(':', '').replace('.', '')}",
        "timestamp": timestamp,
        "source_id": "expedition-hq-dashboard",
        "expedition_id": "expedition-hq-dashboard",
        "event_type": event_type,
        "title": f"Proposal {decision}: {proposal['title']}",
        "summary": (
            f"{proposal['source_agent']} proposal '{proposal['title']}' was marked {proposal['status']}; "
            f"requested soft wager {wager:g} XP, {effect}. Note: {note}"
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
        "tags": ["proposal", "soft-wager", decision] + (["clarification"] if decision == "revise" else []),
        "proposal_id": proposal["proposal_id"],
        "decision_note": note,
}


def proposal_work_start_event(proposal: dict[str, Any]) -> dict[str, Any]:
    timestamp = proposal.get("work_started_at") or _now()
    note = proposal.get("work_start_note") or ""
    return {
        "id": f"evt-proposal-{proposal['proposal_id']}-work-start-{timestamp.replace(':', '').replace('.', '')}",
        "timestamp": timestamp,
        "source_id": "expedition-hq-dashboard",
        "expedition_id": "expedition-hq-dashboard",
        "event_type": "proposal_work_started",
        "title": f"Queued for work: {proposal['title']}",
        "summary": (
            f"Proposal '{proposal['title']}' was moved into the local work queue. "
            f"Actual implementation still requires a separate local work session. Note: {note}"
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
            "Proposal work queue records are local planning markers and do not apply real XP."
        ],
        "tags": ["proposal", "work-start", "local-only"],
        "proposal_id": proposal["proposal_id"],
        "work_start_note": note,
    }


def proposal_implementation_request_event(proposal: dict[str, Any]) -> dict[str, Any]:
    timestamp = proposal.get("implementation_requested_at") or _now()
    return {
        "id": f"evt-proposal-{proposal['proposal_id']}-implementation-request-{timestamp.replace(':', '').replace('.', '')}",
        "timestamp": timestamp,
        "source_id": "expedition-hq-dashboard",
        "expedition_id": "expedition-hq-dashboard",
        "event_type": "proposal_implementation_requested",
        "title": f"Implement proposal: {proposal['title']}",
        "summary": (
            f"Proposal-scoped implementation was authorized for '{proposal['title']}'. "
            "Expedition HQ recorded the OpenClaw route snapshot, provider skips, and local evidence trail."
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
            "handoff_chain": True,
            "polish": False,
            "sentimental_record": False,
        },
        "multiplier_notes": [
            "Implementation requests create local briefs and routing metadata only; no real XP is awarded."
        ],
        "tags": ["proposal", "implementation-request", "local-only", "openclaw-routing"],
        "proposal_id": proposal["proposal_id"],
        "implementation_session_id": proposal.get("implementation_session_id"),
        "implementation_brief_path": proposal.get("implementation_brief_path"),
        "implementation_dispatch_status": proposal.get("implementation_dispatch_status"),
        "implementation_route_plan": proposal.get("implementation_route_plan"),
    }


def proposal_implementation_complete_event(proposal: dict[str, Any]) -> dict[str, Any]:
    timestamp = proposal.get("implementation_completed_at") or _now()
    return {
        "id": f"evt-proposal-{proposal['proposal_id']}-implemented-{timestamp.replace(':', '').replace('.', '')}",
        "timestamp": timestamp,
        "source_id": "expedition-hq-dashboard",
        "expedition_id": "expedition-hq-dashboard",
        "event_type": "proposal_implementation_completed",
        "title": f"Implementation ready for review: {proposal['title']}",
        "summary": (
            f"Implementation for proposal '{proposal['title']}' was marked ready for final review. "
            "August must accept it before the proposal moves to Completed."
        ),
        "status": "review_pending",
        "risk_level": "medium",
        "needs_review": True,
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
            "handoff_chain": True,
            "polish": False,
            "sentimental_record": False,
        },
        "multiplier_notes": [
            "Implementation completion is a review marker and does not award real XP."
        ],
        "tags": ["proposal", "implementation-complete", "final-review"],
        "proposal_id": proposal["proposal_id"],
        "implementation_session_id": proposal.get("implementation_session_id"),
        "implementation_evidence_refs": proposal.get("implementation_evidence_refs", []),
    }


def proposal_implementation_review_event(proposal: dict[str, Any], review_decision: str) -> dict[str, Any]:
    timestamp = proposal.get("implementation_reviewed_at") or _now()
    return {
        "id": f"evt-proposal-{proposal['proposal_id']}-implementation-{review_decision}-{timestamp.replace(':', '').replace('.', '')}",
        "timestamp": timestamp,
        "source_id": proposal.get("implementation_reviewer_id") or "august",
        "expedition_id": "expedition-hq-dashboard",
        "event_type": "proposal_implementation_review",
        "title": f"Implementation {review_decision}: {proposal['title']}",
        "summary": (
            f"Implementation for proposal '{proposal['title']}' was {review_decision}ed by "
            f"{proposal.get('implementation_reviewer_id') or 'august'}. Note: {proposal.get('implementation_review_note') or ''}"
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
            "handoff_chain": True,
            "polish": False,
            "sentimental_record": False,
        },
        "multiplier_notes": [
            "Final proposal review updates simulated proposal wager gain only; real XP remains event-based."
        ],
        "tags": ["proposal", "implementation-review", review_decision],
        "proposal_id": proposal["proposal_id"],
        "implementation_session_id": proposal.get("implementation_session_id"),
        "simulated_xp_gain": proposal.get("simulated_xp_gain", 0.0),
    }


def implementation_route_plan(proposal: dict[str, Any]) -> dict[str, Any]:
    affected = _string_list(proposal.get("affected_areas"))
    candidate_providers = [
        normalize_route_participant(candidate)
        for candidate in DEFAULT_CANDIDATE_PROVIDERS
    ]
    selected_agents = [
        normalize_route_participant(agent)
        for agent in DEFAULT_SELECTED_ROUTE_AGENTS
    ]
    skipped_providers = [
        candidate
        for candidate in candidate_providers
        if candidate.get("route_status") == "skipped" or candidate.get("unavailable_reason")
    ]
    recommended_agents = [
        {
            "agent_id": agent["agent_id"],
            "role": agent["task_role"],
            "reason": agent.get("reason", ""),
        }
        for agent in selected_agents
    ]
    return {
        "orchestration_layer": "OpenClaw",
        "route_snapshot_version": "provider_agnostic_v1",
        "authority_source": "implement_proposal",
        "autonomy_scope": "proposal_scoped",
        "dispatch_mode": "openclaw_provider_agnostic",
        "dispatch_status": "queued",
        "routing_owner": "OpenClaw",
        "primary_provider": "openclaw_router",
        "privacy": "internal",
        "risk": "repo_edit",
        "task_type": "final_implementation",
        "policy_basis": (
            "OpenClaw owns provider routing; Expedition HQ observes route choices, skips, evidence, and outcome."
        ),
        "provider_roles": PROVIDER_ROLES,
        "selected_agents": selected_agents,
        "candidate_providers": candidate_providers,
        "skipped_providers": skipped_providers,
        "provider_result_refs": [],
        "token_saving_choices": [
            "Prefer free or cheap providers for redacted cross-checks, critique, source scouting, and alternate reasoning.",
            "Reserve local trusted Codex/OpenClaw paths for repo edits, private files, test execution, and final synthesis.",
            "Continue with selected local agents when a candidate provider is unavailable or unprofiled.",
        ],
        "promotion_policy": (
            "Unknown providers may contribute cross-reference output first; trusted implementation roles require "
            "useful recorded results and explicit local promotion events."
        ),
        "recommended_agents": recommended_agents,
        "affected_areas": affected,
        "final_reviewer_id": "august",
    }


def normalize_implementation_route_plan(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    recommended_agents = value.get("recommended_agents")
    if isinstance(recommended_agents, list):
        safe_agents = [
            {
                "agent_id": str(agent.get("agent_id") or "").strip(),
                "role": str(agent.get("role") or "").strip(),
                "reason": str(agent.get("reason") or "").strip(),
            }
            for agent in recommended_agents
            if isinstance(agent, dict) and str(agent.get("agent_id") or "").strip()
        ]
    else:
        safe_agents = []
    selected_agents = _route_participant_list(value.get("selected_agents"))
    if not selected_agents and safe_agents:
        selected_agents = _route_participant_list([
            {
                "agent_id": agent.get("agent_id"),
                "task_role": agent.get("role"),
                "reason": agent.get("reason"),
                "route_status": "selected",
            }
            for agent in safe_agents
        ])
    candidate_providers = _route_participant_list(value.get("candidate_providers"))
    skipped_providers = _route_participant_list(value.get("skipped_providers"))
    out = {
        key: value.get(key)
        for key in [
            "orchestration_layer",
            "route_snapshot_version",
            "authority_source",
            "autonomy_scope",
            "dispatch_mode",
            "dispatch_status",
            "routing_owner",
            "primary_provider",
            "privacy",
            "risk",
            "task_type",
            "policy_basis",
            "promotion_policy",
            "dispatch_job_path",
            "dispatch_run_dir",
            "final_reviewer_id",
        ]
        if value.get(key) is not None
    }
    out["provider_roles"] = _string_list(value.get("provider_roles"))
    out["selected_agents"] = selected_agents
    out["candidate_providers"] = candidate_providers
    out["skipped_providers"] = skipped_providers
    out["provider_result_refs"] = _string_list(value.get("provider_result_refs"))
    out["token_saving_choices"] = _string_list(value.get("token_saving_choices"))
    out["recommended_agents"] = safe_agents
    out["affected_areas"] = _string_list(value.get("affected_areas"))
    out["approval_required_for"] = _string_list(value.get("approval_required_for"))
    return out


def normalize_route_participant(value: dict[str, Any]) -> dict[str, Any]:
    agent_id = str(value.get("agent_id") or value.get("provider_id") or value.get("id") or "").strip()
    provider = str(value.get("provider") or value.get("provider_id") or agent_id).strip()
    task_role = str(value.get("task_role") or value.get("role") or "").strip()
    if task_role not in PROVIDER_ROLES:
        task_role = task_role or "research_crosscheck"
    participant = {
        "agent_id": agent_id or provider,
        "provider": provider or agent_id,
        "access_mode": str(value.get("access_mode") or "").strip(),
        "trust_level": str(value.get("trust_level") or "unprofiled_candidate").strip(),
        "task_role": task_role,
        "route_status": str(value.get("route_status") or "candidate").strip(),
        "cost_quota_notes": str(value.get("cost_quota_notes") or "").strip(),
        "unavailable_reason": str(value.get("unavailable_reason") or "").strip(),
        "reason": str(value.get("reason") or "").strip(),
        "result_refs": _string_list(value.get("result_refs")),
        "evidence_refs": _string_list(value.get("evidence_refs")),
        "capabilities": _string_list(value.get("capabilities")),
    }
    return {
        key: item
        for key, item in participant.items()
        if item not in ("", [], None)
    }


def _route_participant_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    participants: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        normalized = normalize_route_participant(item)
        agent_id = normalized.get("agent_id")
        if not agent_id or agent_id in seen:
            continue
        seen.add(agent_id)
        participants.append(normalized)
    return participants


def proposal_implementation_brief(proposal: dict[str, Any]) -> str:
    route_plan = normalize_implementation_route_plan(proposal.get("implementation_route_plan"))
    votes = proposal.get("council_summary", {}).get("vote_counts", {})
    evidence_refs = proposal.get("implementation_evidence_refs", [])
    selected_agents = route_plan.get("selected_agents", [])
    candidate_providers = route_plan.get("candidate_providers", [])
    skipped_providers = route_plan.get("skipped_providers", [])
    return "\n".join([
        f"# Implement Proposal: {proposal['title']}",
        "",
        f"- Proposal ID: `{proposal['proposal_id']}`",
        f"- Implementation session: `{proposal.get('implementation_session_id') or 'not-created'}`",
        f"- Source agent: `{proposal.get('source_agent')}`",
        f"- Proposal type: `{proposal.get('proposal_type')}`",
        f"- Risk level: `{proposal.get('risk_level')}`",
        f"- Estimated active time: `{proposal.get('estimated_active_minutes', 0):g}` minutes",
        f"- Requested soft wager: `{proposal.get('requested_xp_wager', 0):g}` XP",
        f"- Final reviewer: `{route_plan.get('final_reviewer_id') or 'august'}`",
        f"- Dispatch job: `{route_plan.get('dispatch_job_path') or 'not-written-yet'}`",
        "",
        "## Proposal Brief",
        "",
        proposal.get("summary") or "",
        "",
        "## Reasoning",
        "",
        proposal.get("reasoning") or "",
        "",
        "## Acceptance Criteria",
        "",
        *_markdown_list(proposal.get("acceptance_criteria")),
        "",
        "## Rollback Plan",
        "",
        proposal.get("rollback_plan") or "",
        "",
        "## Council Signal",
        "",
        f"- Support: {votes.get('support', 0)}",
        f"- Oppose: {votes.get('oppose', 0)}",
        f"- Abstain: {votes.get('abstain', 0)}",
        "",
        "## OpenClaw Routing Snapshot",
        "",
        f"- Routing owner: `{route_plan.get('routing_owner') or route_plan.get('orchestration_layer') or 'OpenClaw'}`",
        f"- Dispatch mode: `{route_plan.get('dispatch_mode') or 'openclaw_provider_agnostic'}`",
        f"- Dispatch status: `{route_plan.get('dispatch_status') or 'queued'}`",
        f"- Primary router: `{route_plan.get('primary_provider') or 'openclaw_router'}`",
        f"- Policy basis: {route_plan.get('policy_basis') or 'OpenClaw routes; Expedition HQ observes.'}",
        "",
        "Provider roles:",
        "",
        *_markdown_list(route_plan.get("provider_roles")),
        "",
        "Selected route agents:",
        "",
        *_markdown_route_participant_list(selected_agents),
        "",
        "Candidate providers:",
        "",
        *_markdown_route_participant_list(candidate_providers),
        "",
        "Skipped or unavailable providers:",
        "",
        *_markdown_route_participant_list(skipped_providers),
        "",
        "Token-saving choices:",
        "",
        *_markdown_list(route_plan.get("token_saving_choices")),
        "",
        "Promotion policy:",
        "",
        route_plan.get("promotion_policy") or (
            "Candidate providers can support cross-reference first; trusted implementation requires useful evidence."
        ),
        "",
        "## Completion Rule",
        "",
        "Do not move this proposal to Completed directly. After implementation, mark it implemented with evidence. "
        "August is the final reviewer and must accept it before the proposal becomes Completed.",
        "",
        "## Evidence Refs",
        "",
        *(_markdown_list(evidence_refs) if evidence_refs else ["- None yet."]),
        "",
    ])


def _implementation_session_id(proposal_id: str, timestamp: str) -> str:
    safe_timestamp = timestamp.replace(":", "").replace(".", "").replace("+", "")
    return f"impl-{proposal_id}-{safe_timestamp}"


def normalize_work_start_note(value: Any) -> str | None:
    note = str(value or "").strip()
    if not note:
        return None
    if note in LEGACY_WORK_QUEUE_NOTES:
        return DEFAULT_WORK_QUEUE_NOTE
    return note


def _decision_dialogue_messages(
    proposal: dict[str, Any],
    decision: str,
    note: str,
    note_provided: bool,
    timestamp: str,
) -> list[dict[str, Any]]:
    messages = list(proposal.get("dialogue_messages") or [])
    proposal_id = proposal["proposal_id"]
    author_type = "user" if note_provided else "system"
    author_id = "august" if note_provided else "proposal-desk"
    messages.append(_dialogue_message(
        proposal_id,
        author_type,
        author_id,
        note,
        timestamp,
        "decision_note",
        f"{decision}-decision",
    ))

    if decision == "revise":
        for index, question in enumerate(CLARIFICATION_QUESTIONS, start=1):
            messages.append(_dialogue_message(
                proposal_id,
                "agent",
                "proposal-desk",
                question,
                timestamp,
                "clarification_question",
                f"clarification-{index}",
            ))
    return messages


def _work_start_dialogue_messages(
    proposal: dict[str, Any],
    note: str,
    note_provided: bool,
    timestamp: str,
) -> list[dict[str, Any]]:
    messages = list(proposal.get("dialogue_messages") or [])
    messages.append(_dialogue_message(
        proposal["proposal_id"],
        "user" if note_provided else "system",
        "august" if note_provided else "planning-bureau",
        note,
        timestamp,
        "work_start",
        "work-start",
    ))
    return messages


def _implementation_dialogue_messages(
    proposal: dict[str, Any],
    note: str,
    note_provided: bool,
    timestamp: str,
    message_type: str,
    suffix: str,
    *,
    author_id: str | None = None,
) -> list[dict[str, Any]]:
    messages = list(proposal.get("dialogue_messages") or [])
    messages.append(_dialogue_message(
        proposal["proposal_id"],
        "user" if note_provided or author_id else "system",
        author_id or ("august" if note_provided else "planning-bureau"),
        note,
        timestamp,
        message_type,
        suffix,
    ))
    return messages


def _dialogue_message(
    proposal_id: str,
    author_type: str,
    author_id: str,
    message: str,
    created_at: str,
    message_type: str,
    suffix: str,
) -> dict[str, Any]:
    safe_timestamp = created_at.replace(":", "").replace(".", "")
    return {
        "message_id": f"msg-{proposal_id}-{suffix}-{safe_timestamp}",
        "proposal_id": proposal_id,
        "author_type": author_type,
        "author_id": author_id,
        "message": message,
        "created_at": created_at,
        "message_type": message_type,
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _dialogue_messages(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    messages = []
    for item in value:
        if not isinstance(item, dict):
            continue
        message = str(item.get("message") or "").strip()
        if not message:
            continue
        proposal_id = str(item.get("proposal_id") or "").strip()
        created_at = str(item.get("created_at") or _now()).strip()
        message_type = str(item.get("message_type") or "agent_revision_note").strip()
        messages.append({
            "message_id": str(item.get("message_id") or f"msg-{proposal_id}-{len(messages) + 1}").strip(),
            "proposal_id": proposal_id,
            "author_type": str(item.get("author_type") or "system").strip(),
            "author_id": str(item.get("author_id") or "proposal-desk").strip(),
            "message": message,
            "created_at": created_at,
            "message_type": message_type,
        })
    return messages


def _proposal_votes(value: Any, proposal_id: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    votes = []
    seen_agents: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        normalized = normalize_vote(item, proposal_id)
        agent_id = normalized["agent_id"]
        if not agent_id or agent_id in seen_agents:
            continue
        seen_agents.add(agent_id)
        votes.append(normalized)
    return votes


def _required_string(value: Any, default: str) -> str:
    normalized = str(value or "").strip()
    return normalized or default


def _append_note(value: Any, note: str) -> str:
    existing = str(value or "").strip()
    if not existing:
        return note
    if note in existing:
        return existing
    return f"{existing} {note}"


def _markdown_list(items: Any) -> list[str]:
    values = _string_list(items)
    if not values:
        return ["- None."]
    return [f"- {item}" for item in values]


def _markdown_agent_list(items: Any) -> list[str]:
    if not isinstance(items, list) or not items:
        return ["- `coder`: implement the proposal locally, then hand off evidence for review."]
    lines = []
    for item in items:
        if not isinstance(item, dict):
            continue
        agent_id = str(item.get("agent_id") or "").strip()
        role = str(item.get("role") or "").strip()
        reason = str(item.get("reason") or "").strip()
        if not agent_id:
            continue
        detail = role or "participate in implementation routing"
        if reason:
            detail = f"{detail} Reason: {reason}"
        lines.append(f"- `{agent_id}`: {detail}")
    return lines or ["- `coder`: implement the proposal locally, then hand off evidence for review."]


def _markdown_route_participant_list(items: Any) -> list[str]:
    if not isinstance(items, list) or not items:
        return ["- None."]
    lines = []
    for item in items:
        if not isinstance(item, dict):
            continue
        agent_id = str(item.get("agent_id") or "").strip()
        provider = str(item.get("provider") or "").strip()
        task_role = str(item.get("task_role") or "").strip()
        trust = str(item.get("trust_level") or "").strip()
        status = str(item.get("route_status") or "").strip()
        unavailable = str(item.get("unavailable_reason") or "").strip()
        if not agent_id and not provider:
            continue
        label = agent_id or provider
        detail = " / ".join(part for part in [provider, task_role, trust, status] if part)
        if unavailable:
            detail = f"{detail}. Skipped: {unavailable}" if detail else f"Skipped: {unavailable}"
        lines.append(f"- `{label}`: {detail or 'route participant'}")
    return lines or ["- None."]


def _peer_review_xp_multiplier(response_kind: str, value: Any) -> float:
    if response_kind == REQUIRED_ABSTAIN_RESPONSE_KIND:
        return 0.0
    if response_kind == AMENDED_AFTER_PROMPT_RESPONSE_KIND:
        return LATE_PARTICIPATION_XP_MULTIPLIER
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = 1.0
    return min(max(parsed, 0.0), 1.0)


def _add_peer_review_vote(status: dict[str, Any], vote: dict[str, Any]) -> None:
    if vote.get("response_kind") == REQUIRED_ABSTAIN_RESPONSE_KIND:
        return
    status["peer_review_assessment_count"] += 1
    status["peer_review_xp"] += _non_negative(vote.get("peer_review_xp"), 0.0)
    if vote.get("vote") == "abstain":
        status["peer_review_abstain_count"] += 1
    if vote.get("usefulness_status") == "useful":
        status["peer_review_useful_count"] += 1
    if vote.get("usefulness_status") == "pending_outcome":
        status["peer_review_pending_count"] += 1


def _vote_in_season_window(
    vote: dict[str, Any],
    proposal: dict[str, Any],
    season_window: dict[str, Any],
) -> bool:
    timestamp = vote.get("created_at") or proposal.get("decided_at") or proposal.get("updated_at") or proposal.get("created_at")
    return event_in_window({"timestamp": timestamp}, season_window) if timestamp else False


def _peer_review_totals() -> dict[str, Any]:
    return {
        "peer_review_xp": 0.0,
        "peer_review_assessment_count": 0,
        "peer_review_useful_count": 0,
        "peer_review_pending_count": 0,
        "peer_review_abstain_count": 0,
    }


def _empty_peer_review_status(season_window: dict[str, Any] | None = None) -> dict[str, Any]:
    status = _peer_review_totals()
    status["peer_review_scope"] = "current_season" if season_window is not None else "all_time"
    status["peer_review_season"] = season_window.get("season") if season_window else None
    status["peer_review_window_started_at"] = season_window.get("started_at") if season_window else None
    status["peer_review_window_ends_at"] = season_window.get("ends_at") if season_window else None
    status["peer_review_all_time"] = _peer_review_totals()
    return status


def _non_negative(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    return max(0.0, parsed)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
