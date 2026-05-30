from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo
import json
import os
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "config" / "season-policy.seed.json"
DEFAULT_STATE_PATH = ROOT / "data" / "season-state.json"

DEFAULT_FORMULA_VERSION = "xp_calibration_v0_1"
DEFAULT_XP_MODE = "uncapped_calibration"
DEFAULT_XP_LABEL = "Season 0.x - Uncapped Calibration XP"
SEASON_RESET_SOURCE_OF_TRUTH = "windows_task_scheduler"
CODEX_AUTOMATION_ROLE = "audit_report_only"
XP_RESET_AFFECTED_DOMAINS = [
    "xp_current_season_display",
    "xp_season_state",
]
XP_RESET_PRESERVED_DOMAINS = [
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
]
DEFAULT_POLICY = {
    "season_family": "0.x",
    "first_season": "0.1",
    "formula_version": DEFAULT_FORMULA_VERSION,
    "xp_mode": DEFAULT_XP_MODE,
    "label": DEFAULT_XP_LABEL,
    "timezone": "America/Los_Angeles",
    "daily_reset_time": "06:00",
    "pre_restart_started_at": "2026-05-27T19:55:33-07:00",
    "initial_restart_at": "2026-05-30T06:00:00-07:00",
    "reset_mode": "display_current_season_only",
    "scheduler_source_of_truth": SEASON_RESET_SOURCE_OF_TRUTH,
    "codex_automation_role": CODEX_AUTOMATION_ROLE,
    "affected_domains": XP_RESET_AFFECTED_DOMAINS,
    "preserve": XP_RESET_PRESERVED_DOMAINS,
}


def season_state_path() -> Path:
    return Path(os.environ.get("EXPEDITION_HQ_SEASON_STATE_PATH", DEFAULT_STATE_PATH))


def load_season_policy() -> dict[str, Any]:
    policy = dict(DEFAULT_POLICY)
    if CONFIG_PATH.exists():
        loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            policy.update(loaded)
    return policy


def current_season_window(now: str | datetime | None = None) -> dict[str, Any]:
    return season_window_for(now or _configured_now())


def season_window_for(instant: str | datetime | None = None) -> dict[str, Any]:
    policy = load_season_policy()
    tz = _policy_timezone(policy)
    now_local = _coerce_datetime(instant, tz) if instant is not None else datetime.now(tz)
    first_season = str(policy.get("first_season") or DEFAULT_POLICY["first_season"])
    first_number = _season_number(first_season)
    reset_time = str(policy.get("daily_reset_time") or "06:00")
    initial_restart = _coerce_datetime(policy["initial_restart_at"], tz)

    if now_local < initial_restart:
        season_number = first_number
        started_at = _coerce_datetime(policy["pre_restart_started_at"], tz)
        next_reset_at = initial_restart
        status = "restart_pending"
    else:
        elapsed_days = int((now_local - initial_restart).total_seconds() // 86400)
        season_number = first_number + elapsed_days
        started_at = initial_restart + timedelta(days=elapsed_days)
        next_reset_at = started_at + timedelta(days=1)
        status = "active"

    return {
        "season_family": str(policy.get("season_family") or "0.x"),
        "season": _format_season(first_season, season_number),
        "sequence_number": season_number,
        "formula_version": str(policy.get("formula_version") or DEFAULT_FORMULA_VERSION),
        "xp_mode": str(policy.get("xp_mode") or DEFAULT_XP_MODE),
        "label": str(policy.get("label") or DEFAULT_XP_LABEL),
        "timezone": str(policy.get("timezone") or "America/Los_Angeles"),
        "daily_reset_time": reset_time,
        "started_at": _iso(started_at),
        "ends_at": _iso(next_reset_at),
        "next_reset_at": _iso(next_reset_at),
        "reset_mode": str(policy.get("reset_mode") or "display_current_season_only"),
        "scheduler_source_of_truth": str(policy.get("scheduler_source_of_truth") or SEASON_RESET_SOURCE_OF_TRUTH),
        "codex_automation_role": str(policy.get("codex_automation_role") or CODEX_AUTOMATION_ROLE),
        "affected_domains": list(policy.get("affected_domains") or XP_RESET_AFFECTED_DOMAINS),
        "preserve": list(policy.get("preserve") or XP_RESET_PRESERVED_DOMAINS),
        "status": status,
    }


def current_xp_season(now: str | datetime | None = None) -> str:
    return current_season_window(now)["season"]


def current_xp_label(now: str | datetime | None = None) -> str:
    return current_season_window(now)["label"]


def event_in_window(event: dict[str, Any], window: dict[str, Any]) -> bool:
    timestamp = event.get("timestamp")
    if not timestamp:
        return False

    tz = _policy_timezone(load_season_policy())
    observed_at = _coerce_datetime(timestamp, tz)
    started_at = _coerce_datetime(window["started_at"], tz)
    ends_at = _coerce_datetime(window["ends_at"], tz)
    return started_at <= observed_at < ends_at


def filter_events_for_window(
    events: list[dict[str, Any]],
    window: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    active_window = window or current_season_window()
    return [event for event in events if event_in_window(event, active_window)]


def load_season_state() -> dict[str, Any] | None:
    path = season_state_path()
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def reconcile_season_state(
    now: str | datetime | None = None,
    write: bool = False,
) -> dict[str, Any]:
    window = current_season_window(now)
    state = load_season_state()
    changed = state is None or _state_window_key(state) != _state_window_key(window)
    result = {
        "changed": changed,
        "window": window,
        "state_path": str(season_state_path()),
        "previous_state": state,
    }
    if not write:
        return result

    next_state = _next_state(window, state)
    path = season_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(next_state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["state"] = next_state
    return result


def _next_state(window: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    history = list((previous or {}).get("history") or [])
    if previous and _should_archive_previous_state(previous, window):
        history.append({
            "season": previous.get("season"),
            "started_at": previous.get("started_at"),
            "ended_at": window["started_at"],
            "reset_mode": previous.get("reset_mode"),
        })

    return {
        **window,
        "updated_at": _iso(datetime.now(timezone.utc)),
        "history": history,
    }


def _state_window_key(state: dict[str, Any]) -> tuple[str | None, str | None]:
    return state.get("season"), state.get("started_at")


def _should_archive_previous_state(previous: dict[str, Any], window: dict[str, Any]) -> bool:
    if _state_window_key(previous) == _state_window_key(window):
        return False
    if previous.get("status") == "restart_pending" or window.get("status") == "restart_pending":
        return False

    tz = _policy_timezone(load_season_policy())
    previous_started_at = previous.get("started_at")
    window_started_at = window.get("started_at")
    if not previous_started_at or not window_started_at:
        return True
    return _coerce_datetime(window_started_at, tz) > _coerce_datetime(previous_started_at, tz)


def _configured_now() -> str | None:
    return os.environ.get("EXPEDITION_HQ_NOW")


def _policy_timezone(policy: dict[str, Any]) -> tzinfo:
    timezone_name = str(policy.get("timezone") or "America/Los_Angeles")
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        if timezone_name == "America/Los_Angeles":
            return timezone(timedelta(hours=-7), timezone_name)
        return timezone.utc


def _coerce_datetime(value: str | datetime, tz: tzinfo) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        normalized = str(value).strip().replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def _season_number(season: str) -> int:
    try:
        return int(season.split(".")[-1])
    except (ValueError, IndexError):
        return 1


def _format_season(first_season: str, season_number: int) -> str:
    prefix = ".".join(first_season.split(".")[:-1]) or "0"
    return f"{prefix}.{season_number}"


def _iso(value: datetime) -> str:
    return value.isoformat()
