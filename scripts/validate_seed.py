from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
BOOTSTRAP = ROOT / "archive" / "artifacts" / "bootstrap"
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    ".vite",
    "__pycache__",
    ".pytest_cache",
    "data",
    "logs",
    "runtime",
}

required = [
    CONFIG / "agent-roster.seed.json",
    CONFIG / "expeditions.seed.json",
    CONFIG / "events.seed.json",
    CONFIG / "milestones.seed.json",
    BOOTSTRAP / "agent-census-2026-05-27.redacted.json",
]

def main() -> None:
    for path in sorted(iter_json_files()):
        json.loads(path.read_text(encoding="utf-8"))
        print(f"OK {path.relative_to(ROOT)}")

    for path in required:
        if not path.exists():
            raise SystemExit(f"Missing required file: {path}")

    agents = json.loads((CONFIG / "agent-roster.seed.json").read_text(encoding="utf-8"))
    ids = {a["id"] for a in agents}
    for needed in ["openclaw-main", "codex-memory-operator", "home-windows-codex"]:
        if needed not in ids:
            raise SystemExit(f"Missing expected agent: {needed}")
    print("Seed validation complete.")

def iter_json_files():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in files:
            if name.endswith(".json"):
                yield Path(root) / name

if __name__ == "__main__":
    main()
