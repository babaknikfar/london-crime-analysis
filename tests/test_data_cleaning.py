"""Tests for the data cleaning pipeline."""

import pandas as pd
import pytest

from london_crime.data_cleaning import DataCleaner, CleaningReport, LOCATION_PREFIX


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """Small synthetic raw DataFrame mimicking the Police.uk CSV."""
    return pd.DataFrame({
        "Crime ID": ["abc", "def", "", "", "ghi"],
        "Month": ["2025-01", "2025-01", "2025-02", "2025-02", "2025-03"],
        "Reported by": ["Met"] * 5,
        "Falls within": ["Met"] * 5,
        "Longitude": ["-0.1", "-0.2", "-0.3", "-0.4", "-0.5"],
        "Latitude": ["51.5", "51.6", "51.7", "51.8", "51.9"],
        "Location": [
            f"{LOCATION_PREFIX}Alpha St",
            f"{LOCATION_PREFIX}Beta St",
            f"{LOCATION_PREFIX}Gamma St",
            f"{LOCATION_PREFIX}Delta St",
            f"{LOCATION_PREFIX}Epsilon St",
        ],
        "LSOA code": ["E01", "E02", "E03", "E04", "E05"],
        "LSOA name": ["B1", "B2", "B3", "B4", "B5"],
        "Crime type": ["Burglary", "Robbery", "Drugs", "Drugs", "Burglary"],
        "Last outcome category": ["Solved", "Solved", "", "", "Solved"],
        "Context": [""] * 5,
        "source_file": ["2025-01.csv", "2025-01.csv", "2025-02.csv", "2025-02.csv", "2025-03.csv"],
    })


def test_cleaning_report_summary():
    report = CleaningReport(rows_before=10, rows_after=8, columns_before=["a", "b"], columns_after=["a"])
    report.columns_dropped.append("b")
    summary = report.summary()
    assert "Cleaning Report" in summary
    assert "10 → 8" in summary


def test_normalize_empty_strings(raw_df):
    cleaner = DataCleaner(raw_df)
    result = cleaner._normalize_empty_strings(raw_df.copy())
    assert result["Context"].isna().all()
    assert result["Crime ID"].isna().sum() == 2


def test_drop_constant_and_empty_columns(raw_df):
    cleaner = DataCleaner(raw_df)
    df = cleaner._normalize_empty_strings(raw_df.copy())
    result = cleaner._drop_constant_and_empty_columns(df)
    assert "Reported by" not in result.columns
    assert "Falls within" not in result.columns
    assert "Context" not in result.columns
    dropped = set(cleaner.report.columns_dropped)
    assert {"Reported by", "Falls within", "Context"}.issubset(dropped)


def test_convert_month_to_datetime(raw_df):
    cleaner = DataCleaner(raw_df)
    result = cleaner._convert_month_to_datetime(raw_df.copy())
    assert pd.api.types.is_datetime64_any_dtype(result["Month"])
    assert result["Month"].iloc[0] == pd.Timestamp("2025-01-01")


def test_convert_lat_lon_to_float(raw_df):
    cleaner = DataCleaner(raw_df)
    result = cleaner._convert_lat_lon_to_float(raw_df.copy())
    assert result["Latitude"].dtype == "float64"
    assert result["Longitude"].dtype == "float64"
    assert result["Latitude"].iloc[0] == pytest.approx(51.5)


def test_strip_location_prefix(raw_df):
    cleaner = DataCleaner(raw_df)
    result = cleaner._strip_location_prefix(raw_df.copy())
    assert result["Location"].iloc[0] == "Alpha St"
    assert result["Location"].iloc[1] == "Beta St"
    assert not result["Location"].str.startswith(LOCATION_PREFIX).any()


def test_convert_to_category(raw_df):
    cleaner = DataCleaner(raw_df)
    result = cleaner._convert_to_category(raw_df.copy())
    assert isinstance(result["Crime type"].dtype, pd.CategoricalDtype)
    assert isinstance(result["LSOA code"].dtype, pd.CategoricalDtype)


def test_add_is_anonymized_flag(raw_df):
    cleaner = DataCleaner(raw_df)
    df = cleaner._normalize_empty_strings(raw_df.copy())
    result = cleaner._add_is_anonymized_flag(df)
    assert result["is_anonymized"].sum() == 2
    assert result["is_anonymized"].dtype == bool


def test_drop_exact_duplicate_rows_keeps_nan_id_rows():
    """Critical: rows with NaN Crime ID must NOT be deduplicated against each other."""
    df = pd.DataFrame({
        "Crime ID": [None, None, "x", "x"],
        "Month": ["2025-01"] * 4,
        "Crime type": ["A"] * 4,
    })
    cleaner = DataCleaner(df)
    result = cleaner._drop_exact_duplicate_rows(df)
    # Both NaN rows kept, one of the "x" rows dropped
    assert len(result) == 3


def test_full_clean_pipeline(raw_df):
    cleaner = DataCleaner(raw_df)
    df_clean, report = cleaner.clean()
    assert len(df_clean) == len(raw_df)
    assert "Crime ID" not in df_clean.columns
    assert "Context" not in df_clean.columns
    assert "is_anonymized" in df_clean.columns
    assert pd.api.types.is_datetime64_any_dtype(df_clean["Month"])