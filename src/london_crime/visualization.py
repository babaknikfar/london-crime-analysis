"""Visualization functions for Police.uk crime data."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from london_crime.config import config
from london_crime.logging_config import get_logger

logger = get_logger(__name__)

# Global style
sns.set_theme(style="whitegrid", context="notebook")
DPI = config.eda.get("figure_dpi", 150)
FMT = config.eda.get("figure_format", "png")


def _save(fig: plt.Figure, name: str) -> Path:
    """Save a figure to outputs/figures/ and return the path."""
    path = config.paths.figures_dir / f"{name}.{FMT}"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved figure: {path.relative_to(config.paths.project_root)}")
    return path


def plot_crime_type_counts(counts: pd.Series, top_n: int = 14) -> Path:
    """Horizontal bar chart of crime type counts."""
    fig, ax = plt.subplots(figsize=(10, 6))
    data = counts.head(top_n).sort_values()
    ax.barh(data.index, data.values, color="#c0392b")
    ax.set_xlabel("Number of incidents")
    ax.set_title(f"Top {top_n} Crime Types (2025)", fontsize=14, fontweight="bold")
    for i, v in enumerate(data.values):
        ax.text(v, i, f" {v:,}", va="center", fontsize=9)
    return _save(fig, "crime_type_counts")


def plot_monthly_trend(monthly: pd.Series) -> Path:
    """Line chart of monthly incident totals."""
    fig, ax = plt.subplots(figsize=(11, 5))
    x = monthly.index.astype(str)
    ax.plot(x, monthly.values, marker="o", linewidth=2, color="#2980b9")
    ax.set_ylabel("Incidents")
    ax.set_title("Monthly Crime Incidents (2025)", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, alpha=0.3)
    return _save(fig, "monthly_trend")


def plot_top_lsoas(top: pd.Series) -> Path:
    """Horizontal bar chart of top LSOAs by incident count."""
    fig, ax = plt.subplots(figsize=(10, 6))
    data = top.sort_values()
    ax.barh(data.index, data.values, color="#8e44ad")
    ax.set_xlabel("Incidents")
    ax.set_title("Top 10 LSOAs by Crime Count (2025)", fontsize=14, fontweight="bold")
    return _save(fig, "top_lsoas")


def plot_anonymization_heatmap(table: pd.DataFrame) -> Path:
    """Heatmap of anonymization rate by crime type."""
    fig, ax = plt.subplots(figsize=(7, 8))
    sns.heatmap(
        table,
        annot=True,
        fmt=".1f",
        cmap="Reds",
        cbar_kws={"label": "% anonymized"},
        ax=ax,
    )
    ax.set_title("Anonymization Rate by Crime Type (%)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Is anonymized")
    ax.set_ylabel("")
    return _save(fig, "anonymization_heatmap")


def plot_top_locations(top: pd.Series) -> Path:
    """Horizontal bar chart of top location strings."""
    fig, ax = plt.subplots(figsize=(10, 7))
    data = top.sort_values()
    ax.barh(data.index, data.values, color="#16a085")
    ax.set_xlabel("Incidents")
    ax.set_title("Top 20 Reported Locations (2025)", fontsize=14, fontweight="bold")
    return _save(fig, "top_locations")