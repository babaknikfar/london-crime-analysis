"""
One-time script: combine monthly Police.uk CSV files into a single master CSV.

Reads all *.csv files from data/raw/monthly/, concatenates them,
sorts by Month, and writes data/raw/london_crimes.csv.

Usage (from project root):
    python scripts/combine_monthly_csvs.py
"""

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MONTHLY_DIR = PROJECT_ROOT / "data" / "raw" / "monthly"
OUTPUT_CSV = PROJECT_ROOT / "data" / "raw" / "london_crimes.csv"


def combine_monthly_csvs() -> None:
    """Read all monthly CSVs, concatenate, and save as one file."""
    csv_files = sorted(MONTHLY_DIR.rglob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {MONTHLY_DIR}")
        sys.exit(1)

    print(f"Found {len(csv_files)} monthly CSV files")

    frames = []
    for path in csv_files:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        df["source_file"] = path.name
        frames.append(df)
        print(f"  Loaded {path.relative_to(MONTHLY_DIR)}: {len(df):,} rows")

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(["Month"]).reset_index(drop=True)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_CSV, index=False)

    print(f"\nCombined: {len(combined):,} rows, {combined.shape[1]} columns")
    print(f"Written to: {OUTPUT_CSV}")


if __name__ == "__main__":
    combine_monthly_csvs()