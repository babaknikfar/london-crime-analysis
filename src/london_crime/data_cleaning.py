"""
Data cleaning module for the Metropolitan Police street-level crime dataset.

Takes the raw combined CSV (loaded as strings) and produces a cleaned
DataFrame with proper dtypes, normalized values, and documented decisions.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from london_crime.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CleaningReport:
    """Records what a cleaning run did, for reporting and auditing."""
    rows_before: int = 0
    rows_after: int = 0
    columns_before: list[str] = field(default_factory=list)
    columns_after: list[str] = field(default_factory=list)
    columns_dropped: list[str] = field(default_factory=list)
    columns_converted: dict[str, str] = field(default_factory=dict)
    columns_stripped_prefix: dict[str, str] = field(default_factory=dict)
    derived_columns: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """Human-readable summary of the cleaning run."""
        lines = [
            "Cleaning Report",
            "=" * 60,
            f"Rows:    {self.rows_before:,} → {self.rows_after:,}",
            f"Columns: {len(self.columns_before)} → {len(self.columns_after)}",
            "",
            f"Dropped columns ({len(self.columns_dropped)}): "
            + ", ".join(self.columns_dropped),
            f"Derived columns: " + ", ".join(self.derived_columns),
            f"Stripped prefixes: "
            + ", ".join(f"{c}: '{p}'" for c, p in self.columns_stripped_prefix.items()),
            "",
            "Notes:",
        ]
        lines += [f"  - {note}" for note in self.notes]
        return "\n".join(lines)



# The "On or near " prefix Police.uk adds to anonymized location strings.
LOCATION_PREFIX = "On or near "


class DataCleaner:
    """
    Cleans the raw Metropolitan Police street-level crime DataFrame.

    The cleaning pipeline is applied via `clean()`, which runs each
    transformation method in order and records decisions in a
    CleaningReport.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initialize the cleaner with a raw DataFrame.

        Args:
            df: Raw DataFrame as loaded from the combined CSV,
                with all columns as strings and empty strings preserved.
        """
        self.raw_df = df
        self.report = CleaningReport()

    def clean(self) -> tuple[pd.DataFrame, CleaningReport]:
        """Run the full cleaning pipeline."""
        self.report.rows_before = len(self.raw_df)
        self.report.columns_before = list(self.raw_df.columns)

        df = self.raw_df.copy()

        df = self._normalize_empty_strings(df)
        df = self._drop_constant_and_empty_columns(df)
        df = self._convert_month_to_datetime(df)
        df = self._convert_lat_lon_to_float(df)
        df = self._strip_location_prefix(df)
        df = self._convert_to_category(df)
        df = self._add_is_anonymized_flag(df)
        df = self._drop_exact_duplicate_rows(df)   # ← new, last
        df = self._drop_crime_id_column(df)        # ← new, very last

        self.report.rows_after = len(df)
        self.report.columns_after = list(df.columns)

        return df, self.report

    # --- Individual transformation steps ---

    def _normalize_empty_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Replace empty strings with pd.NA across all object columns."""
        object_cols = df.select_dtypes(include=["object", "str", "string"]).columns
        empty_counts_before = (df[object_cols] == "").sum().sum()

        df[object_cols] = df[object_cols].replace("", pd.NA)

        self.report.notes.append(
            f"Normalized {empty_counts_before:,} empty strings to pd.NA "
            f"across {len(object_cols)} columns"
        )
        return df

    def _drop_constant_and_empty_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop columns that are either fully empty or contain a single value."""
        to_drop: list[str] = []

        for col in df.columns:
            if df[col].isna().all():
                to_drop.append(col)
                self.report.notes.append(f"Dropped '{col}': 100% empty")
            elif df[col].nunique(dropna=True) == 1:
                to_drop.append(col)
                value = df[col].dropna().iloc[0]
                self.report.notes.append(
                    f"Dropped '{col}': constant value '{value}'"
                )

        df = df.drop(columns=to_drop)
        self.report.columns_dropped.extend(to_drop)
        return df

    def _convert_month_to_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert the 'Month' column from 'YYYY-MM' strings to datetime."""
        df["Month"] = pd.to_datetime(df["Month"], format="%Y-%m")
        self.report.columns_converted["Month"] = "str → datetime64[ns]"
        self.report.notes.append(
            "Converted 'Month' from 'YYYY-MM' string to datetime"
        )
        return df

    def _convert_lat_lon_to_float(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert Latitude/Longitude from strings to floats."""
        for col in ("Latitude", "Longitude"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                self.report.columns_converted[col] = "str → float64"
        self.report.notes.append(
            "Converted 'Latitude' and 'Longitude' from strings to floats"
        )
        return df

    def _strip_location_prefix(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove the 'On or near ' prefix from the Location column."""
        if "Location" not in df.columns:
            return df

        has_prefix = df["Location"].str.startswith(LOCATION_PREFIX, na=False)
        count = int(has_prefix.sum())

        df["Location"] = df["Location"].str.removeprefix(LOCATION_PREFIX)

        self.report.columns_stripped_prefix["Location"] = LOCATION_PREFIX
        self.report.notes.append(
            f"Stripped '{LOCATION_PREFIX}' prefix from {count:,} Location values"
        )
        return df

    def _convert_to_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert low-cardinality string columns to pandas 'category' dtype."""
        for col in ("Crime type", "LSOA code", "LSOA name", "source_file"):
            if col in df.columns:
                n_unique = df[col].nunique(dropna=True)
                df[col] = df[col].astype("category")
                self.report.columns_converted[col] = f"str → category ({n_unique} levels)"
        self.report.notes.append(
            "Converted categorical string columns to pandas 'category' dtype"
        )
        return df

    def _add_is_anonymized_flag(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add a boolean column flagging records with redacted Crime ID."""
        if "Crime ID" not in df.columns:
            return df

        df["is_anonymized"] = df["Crime ID"].isna()
        n_anon = int(df["is_anonymized"].sum())
        self.report.derived_columns.append("is_anonymized")
        self.report.notes.append(
            f"Added 'is_anonymized' flag: {n_anon:,} records "
            f"({n_anon / len(df) * 100:.2f}%) are privacy-redacted"
        )
        return df


    def _drop_exact_duplicate_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop rows that are exact duplicates across all columns.
        
        Rows with missing Crime ID are excluded from deduplication —
        they lack an identifier, and pandas treats all-NaN as equal,
        which would falsely collapse distinct anonymized incidents.
        """
        if "Crime ID" not in df.columns:
            return df
        
        has_id = df["Crime ID"].notna()
        
        # Dedup only among rows that have a Crime ID
        df_with_id = df[has_id].drop_duplicates(keep="first")
        df_without_id = df[~has_id]
        
        before = len(df)
        df = pd.concat([df_with_id, df_without_id], ignore_index=True)
        removed = before - len(df)
        
        self.report.notes.append(
            f"Dropped {removed:,} exact duplicate rows "
            f"(among rows with non-null Crime ID, keep='first')"
        )
        return df


    def _drop_crime_id_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop the Crime ID column — proven unreliable as a unique key."""
        if "Crime ID" not in df.columns:
            return df

        df = df.drop(columns=["Crime ID"])
        self.report.columns_dropped.append("Crime ID")
        self.report.notes.append(
            "Dropped 'Crime ID': not a reliable unique key "
            "(4,513 duplicate groups identified); no analytical value"
        )
        return df