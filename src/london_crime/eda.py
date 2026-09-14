"""Exploratory data analysis for cleaned Police.uk crime data."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from london_crime.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class EDAResults:
    """Container for EDA findings."""
    crime_type_counts: pd.Series = field(default_factory=pd.Series)
    top_lsoas: pd.Series = field(default_factory=pd.Series)
    monthly_totals: pd.Series = field(default_factory=pd.Series)
    anonymized_by_crime_type: pd.DataFrame = field(default_factory=pd.DataFrame)
    location_top: pd.Series = field(default_factory=pd.Series)


class EDA:
    """Runs exploratory analysis on the cleaned crime DataFrame."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.results = EDAResults()

    def run_all(self) -> EDAResults:
        """Run every EDA step."""
        self.results.crime_type_counts = self._crime_type_counts()
        self.results.top_lsoas = self._top_lsoas()
        self.results.monthly_totals = self._monthly_totals()
        self.results.anonymized_by_crime_type = self._anonymized_by_crime_type()
        self.results.location_top = self._top_locations()
        return self.results

    def _crime_type_counts(self) -> pd.Series:
        counts = self.df["Crime type"].value_counts()
        logger.info(f"Crime types: {len(counts)}; top = {counts.index[0]} ({counts.iloc[0]:,})")
        return counts

    def _top_lsoas(self, n: int = 10) -> pd.Series:
        counts = self.df["LSOA name"].value_counts().head(n)
        logger.info(f"Top LSOA: {counts.index[0]} ({counts.iloc[0]:,})")
        return counts

    def _monthly_totals(self) -> pd.Series:
        totals = self.df.groupby(self.df["Month"].dt.to_period("M"), observed=True).size()
        logger.info(f"Months: {len(totals)}; range {totals.min():,}-{totals.max():,}")
        return totals

    def _anonymized_by_crime_type(self) -> pd.DataFrame:
        table = pd.crosstab(
            self.df["Crime type"],
            self.df["is_anonymized"],
            normalize="index",
        ) * 100
        logger.info("Anonymization rate by crime type computed")
        return table

    def _top_locations(self, n: int = 20) -> pd.Series:
        counts = self.df["Location"].value_counts().head(n)
        logger.info(f"Top location: {counts.index[0]} ({counts.iloc[0]:,})")
        return counts