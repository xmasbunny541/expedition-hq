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
        "xp": 0
    }
    path = REPORT_DIR / f"{now.strftime('%Y-%m-%d')}-{report['id']}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path)

if __name__ == "__main__":
    main()
