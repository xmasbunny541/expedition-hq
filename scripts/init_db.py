from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from expedition_hq_api.db import seed_db

if __name__ == "__main__":
    seed_db(force=True)
    print("Expedition HQ database initialized from seed files.")
