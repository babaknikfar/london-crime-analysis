"""Feature engineering for Police.uk crime data."""

import pandas as pd

from london_crime.logging_config import get_logger

logger = get_logger(__name__)


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive year, month, day-of-week, quarter, and season from Month."""
    df = df.copy()
    df["year"] = df["Month"].dt.year
    df["month_num"] = df["Month"].dt.month
    df["quarter"] = df["Month"].dt.quarter

    # Season (meteorological)
    season_map = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn",
    }
    df["season"] = df["month_num"].map(season_map).astype("category")

    logger.info("Added temporal features: year, month_num, quarter, season")
    return df


LONDON_BOROUGHS = {
    "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley",
    "Camden", "City of London", "Croydon", "Ealing", "Enfield",
    "Greenwich", "Hackney", "Hammersmith and Fulham", "Haringey",
    "Harrow", "Havering", "Hillingdon", "Hounslow", "Islington",
    "Kensington and Chelsea", "Kingston upon Thames", "Lambeth",
    "Lewisham", "Merton", "Newham", "Redbridge", "Richmond upon Thames",
    "Southwark", "Sutton", "Tower Hamlets", "Waltham Forest",
    "Wandsworth", "Westminster",
}


def add_spatial_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive borough from LSOA name and flag London vs non-London."""
    df = df.copy()
    df["borough"] = (
        df["LSOA name"].astype(str).str.rsplit(" ", n=1).str[0].astype("category")
    )
    df["is_london_borough"] = df["borough"].astype(str).isin(LONDON_BOROUGHS)

    n_london = int(df["is_london_borough"].sum())
    logger.info(
        f"Added borough: {df['borough'].nunique()} unique; "
        f"{n_london:,} rows ({n_london / len(df) * 100:.1f}%) in London boroughs"
    )
    return df


def add_location_features(df: pd.DataFrame) -> pd.DataFrame:
    """Flag generic/placeholder locations."""
    generic_terms = {
        "Supermarket", "Parking Area", "Retail Park", "Shopping Area",
        "Petrol Station", "Bus Stop", "Train Station", "Sports Centre",
        "Nightclub", "Public House", "Hospital", "School",
    }
    df = df.copy()
    df["is_generic_location"] = df["Location"].isin(generic_terms)
    n = int(df["is_generic_location"].sum())
    logger.info(f"Added is_generic_location: {n:,} rows ({n / len(df) * 100:.1f}%)")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run all feature engineering steps."""
    df = add_temporal_features(df)
    df = add_spatial_features(df)
    df = add_location_features(df)
    return df