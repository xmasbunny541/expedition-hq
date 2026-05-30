from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from expedition_hq_api.season import reconcile_season_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reconcile the local Expedition HQ Season 0.x display window."
    )
    parser.add_argument("--apply", action="store_true", help="Write data/season-state.json when the active window changed.")
    parser.add_argument("--now", help="ISO timestamp override for deterministic tests or manual backfill.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = reconcile_season_state(now=args.now, write=args.apply)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
