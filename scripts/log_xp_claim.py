from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_ENDPOINT = "http://127.0.0.1:8789/xp-claims"


def parse_multiplier(value: str) -> tuple[str, float]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("multipliers must use key=value")
    key, raw = value.split("=", 1)
    key = key.strip()
    if not key:
        raise argparse.ArgumentTypeError("multiplier key cannot be empty")
    try:
        return key, float(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid multiplier value: {raw}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Submit a local Season 0.x XP claim to Expedition HQ."
    )
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--id")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-project")
    parser.add_argument("--expedition-id", required=True)
    parser.add_argument("--event-type", default="cross_project_work")
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--status", default="success")
    parser.add_argument("--risk-level", default="low")
    parser.add_argument("--active-minutes", type=float, required=True)
    parser.add_argument("--xp-confidence", default="estimated")
    parser.add_argument("--party-agent", action="append", default=[])
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--artifact-ref", action="append", default=[])
    parser.add_argument("--field-report-path")
    parser.add_argument("--decision-record-ref")
    parser.add_argument("--test-output-ref")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--multiplier", action="append", type=parse_multiplier, default=[])
    parser.add_argument(
        "--stress-missing-evidence",
        action="store_true",
        help="Allow a nonzero claim with no evidence so Season 0.x can flag it.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    has_evidence = any([
        args.evidence,
        args.artifact_ref,
        args.field_report_path,
        args.decision_record_ref,
        args.test_output_ref,
    ])
    if args.active_minutes > 0 and not has_evidence and not args.stress_missing_evidence:
        parser.error("nonzero XP claims need evidence, or use --stress-missing-evidence for a deliberate 0.x probe")

    payload = {
        "source_id": args.source_id,
        "source_project": args.source_project,
        "expedition_id": args.expedition_id,
        "event_type": args.event_type,
        "title": args.title,
        "summary": args.summary,
        "status": args.status,
        "risk_level": args.risk_level,
        "active_minutes": args.active_minutes,
        "xp_confidence": args.xp_confidence,
        "party_agents": args.party_agent,
        "evidence_refs": args.evidence,
        "artifact_refs": args.artifact_ref,
        "field_report_path": args.field_report_path,
        "decision_record_ref": args.decision_record_ref,
        "test_output_ref": args.test_output_ref,
        "scoring_multipliers": dict(args.multiplier),
        "tags": args.tag,
    }
    if args.id:
        payload["id"] = args.id

    payload = {key: value for key, value in payload.items() if value not in (None, [], {})}

    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    body = json.dumps(payload).encode("utf-8")
    request = Request(
        args.endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            print(response.read().decode("utf-8"))
            return 0
    except HTTPError as exc:
        print(exc.read().decode("utf-8"), file=sys.stderr)
        return 1
    except URLError as exc:
        print(f"could not reach Expedition HQ API: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
