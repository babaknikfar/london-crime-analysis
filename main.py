"""
End-to-end pipeline for Police.uk crime data analysis.

Usage:
    python main.py
"""

import sys
from pathlib import Path

import pandas as pd

from london_crime.config import config
from london_crime.data_cleaning import DataCleaner
from london_crime.eda import EDA
from london_crime.features import engineer_features
from london_crime.logging_config import get_logger
from london_crime.visualization import (
    plot_anonymization_heatmap,
    plot_crime_type_counts,
    plot_monthly_trend,
    plot_top_locations,
    plot_top_lsoas,
)

logger = get_logger("main")


def load_raw() -> pd.DataFrame:
    path = config.paths.raw_data_dir / config.data["raw_filename"]
    logger.info(f"Loading raw: {path.name}")
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def run_pipeline() -> None:
    logger.info("=== Pipeline started ===")

    # 1. Load
    df_raw = load_raw()

    # 2. Clean
    df_clean, report = DataCleaner(df_raw).clean()
    print(report.summary())

    # 3. Save cleaned
    cleaned_path = config.paths.processed_data_dir / config.data["cleaned_filename"]
    df_clean.to_parquet(cleaned_path, index=False)
    logger.info(f"Saved cleaned: {cleaned_path.name}")

    # 4. Features
    df_features = engineer_features(df_clean)
    features_path = config.paths.processed_data_dir / "london_crimes_features.parquet"
    df_features.to_parquet(features_path, index=False)
    logger.info(f"Saved features: {features_path.name}")

    # 5. EDA
    eda = EDA(df_clean)
    results = eda.run_all()

    # 6. Figures
    plot_crime_type_counts(results.crime_type_counts)
    plot_monthly_trend(results.monthly_totals)
    plot_top_lsoas(results.top_lsoas)
    plot_anonymization_heatmap(results.anonymized_by_crime_type)
    plot_top_locations(results.location_top)

    # 7. Reports
    from scripts.generate_reports import generate_eda_report, generate_hypothesis_report
    generate_eda_report(df_clean, config.paths.reports_dir / "eda_report.md")
    generate_hypothesis_report(df_clean, config.paths.reports_dir / "hypothesis_report.md")

    logger.info("=== Pipeline complete ===")


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        sys.exit(1)