"""Statistical hypothesis testing for Police.uk crime data."""

from dataclasses import dataclass, field

import pandas as pd
from scipy import stats

from london_crime.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class HypothesisResult:
    """Outcome of a statistical test."""
    name: str
    statistic: float
    p_value: float
    conclusion: str
    details: dict = field(default_factory=dict)


def test_seasonal_uniformity(df: pd.DataFrame) -> HypothesisResult:
    """H1: Monthly incident counts follow a uniform distribution."""
    monthly = df.groupby(df["Month"].dt.month, observed=True).size()
    chi2, p = stats.chisquare(monthly.values)
    conclusion = (
        "Reject H0: monthly counts are NOT uniform (seasonal pattern exists)"
        if p < 0.05 else "Fail to reject H0: monthly counts are consistent with uniform"
    )
    logger.info(f"Seasonal test: chi2={chi2:.2f}, p={p:.2e}")
    return HypothesisResult("Seasonal uniformity", float(chi2), float(p), conclusion)


def test_crime_type_independence_from_anonymization(df: pd.DataFrame) -> HypothesisResult:
    """H2: Crime type is independent of anonymization status."""
    table = pd.crosstab(df["Crime type"], df["is_anonymized"])
    chi2, p, dof, _ = stats.chi2_contingency(table)
    conclusion = (
        "Reject H0: crime type and anonymization are NOT independent"
        if p < 0.05 else "Fail to reject H0: crime type and anonymization are independent"
    )
    logger.info(f"Independence test: chi2={chi2:.2f}, p={p:.2e}, dof={dof}")
    return HypothesisResult(
        "Crime type × Anonymization independence",
        float(chi2), float(p), conclusion, {"dof": dof},
    )


def test_top_lsoa_vs_rest(df: pd.DataFrame) -> HypothesisResult:
    """H3: Top-LSOA crime mix differs from the rest of the dataset."""
    top = df[df["LSOA name"] == "Westminster 013G"]
    rest = df[df["LSOA name"] != "Westminster 013G"]

    table = pd.crosstab(
        pd.concat([top["Crime type"], rest["Crime type"]], ignore_index=True),
        ["top"] * len(top) + ["rest"] * len(rest),
    )
    chi2, p, dof, _ = stats.chi2_contingency(table)

    conclusion = (
        "Reject H0: top LSOA has a different crime type distribution"
        if p < 0.05 else "Fail to reject H0: distributions are similar"
    )
    logger.info(f"LSOA mix test: chi2={chi2:.2f}, p={p:.2e}, dof={dof}")
    return HypothesisResult("Top LSOA crime mix", float(chi2), float(p), conclusion, {"dof": dof})


def run_all(df: pd.DataFrame) -> list[HypothesisResult]:
    """Run every hypothesis test."""
    return [
        test_seasonal_uniformity(df),
        test_crime_type_independence_from_anonymization(df),
        test_top_lsoa_vs_rest(df),
    ]