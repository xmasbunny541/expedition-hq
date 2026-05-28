from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "archive" / "field-reports"

def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    report = {
        "id": f"field-report-{uuid4().hex[:8]}",
        "timestamp": now.isoformat(),
        "expedition_id": "expedition-hq-dashboard",
        "source_id": "manual",
        "title": "Manual field report",
        "summary": "Replace this with what changed, what was learned, and what artifact proves progress.",
        "artifact_refs": [],
        "sentimental_note": "",
        "xp_season": "0.1",
        "formula_version": "xp_calibration_v0_1",
        "xp_mode": "uncapped_calibration",
        "active_minutes": 0,
        "xp_confidence": "estimated",
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
        "shadow_multiplier_notes": [],
        "multiplier_notes": []
    }
    path = REPORT_DIR / f"{now.strftime('%Y-%m-%d')}-{report['id']}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path)

if __name__ == "__main__":
    main()
