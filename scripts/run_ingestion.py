import argparse
from pathlib import Path
import sys

# Ensure project root is on path for `src.*` imports, and src/ for the
# unprefixed intra-package imports used inside the modules.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.common.console import configure_console
from src.ingestion.ingest import main as run_ingestion

configure_console()


def parse_args():
    parser = argparse.ArgumentParser(description="Run CRC ingestion")
    parser.add_argument("--client", required=True, help="Client name (e.g. CLT_KAGGLE_TEST)")
    parser.add_argument("--pilot", required=True, help="Pilot name (e.g. PILOT_001_2026_03_26)")
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"Running ingestion for:")
    print(f"Client: {args.client}")
    print(f"Pilot: {args.pilot}")

    run_ingestion(client=args.client, pilot=args.pilot)


if __name__ == "__main__":
    main()