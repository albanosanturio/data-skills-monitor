# Load a parsed jobs JSON export into the Supabase `jobs` table.
#
# Decoupled from parse_htmls.py on purpose: the JSON export is the contract
# between parsing and loading, so a failed/re-run DB load never needs to
# re-parse or re-move the source HTML files.
#
# Usage:
#   python -m src.indeed_jobs.load_to_db   #loads the most recent export
#   python -m src.indeed_jobs.load_to_db data/exports/jobs_export_20260808_120000.json

import sys
from pathlib import Path
import json
import logging

# Add project root to path (same pattern as parse_htmls.py)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.indeed_jobs.utils import insert_to_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

exports_dir = Path('data/exports/')


def latest_export(exports_dir: Path) -> Path:
    """Return the most recently written jobs_export_*.json in exports_dir."""
    exports = sorted(exports_dir.glob('jobs_export_*.json'))
    if not exports:
        raise FileNotFoundError(f"No exports found in {exports_dir}")
    return exports[-1]


def load_export(json_path: Path) -> list:
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_export(exports_dir)
    logger.info(f"Loading export: {json_path}")

    jobs_list = load_export(json_path)
    logger.info(f"{len(jobs_list)} jobs read from export")

    if not jobs_list:
        logger.warning("Export is empty, nothing to load.")
        return

    summary = insert_to_db(jobs_list)
    logger.info(f"Load complete: {summary}")


if __name__ == "__main__":
    main()