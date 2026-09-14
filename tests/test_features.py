"""Tests for feature engineering."""

import pandas as pd
import pytest

from london_crime.features import (
    add_temporal_features,
    add_spatial_features,
    add_location_features,
    engineer_features,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "Month": pd.to_datetime(["2025-01-01", "2025-07-01", "2025-12-01"]),
        "LSOA name": ["Westminster 013G", "Camden 001A", "Arun 004A"],
        "Location": ["Supermarket", "Alpha Street", "Parking Area"],
        "Crime type": ["Burglary", "Robbery", "Drugs"],
    })


def test_add_temporal_features(sample_df):
    result = add_temporal_features(sample_df)
    assert "season" in result.columns
    assert result["season"].iloc[0] == "Winter"
    assert result["season"].iloc[1] == "Summer"
    assert result["quarter"].iloc[0] == 1


def test_add_spatial_features(sample_df):
    result = add_spatial_features(sample_df)
    assert "borough" in result.columns
    assert "is_london_borough" in result.columns
    assert result["borough"].iloc[0] == "Westminster"
    assert result["is_london_borough"].iloc[0] == True
    assert result["is_london_borough"].iloc[2] == False  # Arun not in London


def test_add_location_features(sample_df):
    result = add_location_features(sample_df)
    assert "is_generic_location" in result.columns
    assert result["is_generic_location"].iloc[0] == True   # Supermarket
    assert result["is_generic_location"].iloc[1] == False  # Alpha Street
    assert result["is_generic_location"].iloc[2] == True   # Parking Area


def test_engineer_features(sample_df):
    result = engineer_features(sample_df)
    expected = {"year", "month_num", "quarter", "season", "borough",
                "is_london_borough", "is_generic_location"}
    assert expected.issubset(result.columns)