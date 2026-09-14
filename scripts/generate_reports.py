"""Generate markdown reports from EDA results."""

from pathlib import Path
import pandas as pd

from london_crime.config import config
from london_crime.eda import EDA
from london_crime.logging_config import get_logger

from london_crime.hypothesis_testing import run_all as run_hypotheses


logger = get_logger(__name__)


def generate_eda_report(df: pd.DataFrame, out_path: Path) -> None:
    """Write a markdown EDA summary."""
    eda = EDA(df)
    r = eda.run_all()

    lines = [
        "# EDA Report — Metropolitan Police Crime Incidents (2025)",
        "",
        "## Dataset Overview",
        f"- **Rows:** {len(df):,}",
        f"- **Columns:** {df.shape[1]}",
        f"- **Date range:** {df['Month'].min().date()} → {df['Month'].max().date()}",
        f"- **Distinct LSOAs:** {df['LSOA name'].nunique():,}",
        f"- **Anonymized records:** {df['is_anonymized'].sum():,} "
        f"({df['is_anonymized'].mean() * 100:.2f}%)",
        "",
        "## Crime Type Distribution",
        "",
        "| Crime Type | Incidents | % |",
        "|---|---:|---:|",
    ]
    total = r.crime_type_counts.sum()
    for ct, count in r.crime_type_counts.items():
        lines.append(f"| {ct} | {count:,} | {count / total * 100:.2f} |")

    lines += [
        "",
        "## Monthly Trend",
        "",
        "| Month | Incidents |",
        "|---|---:|",
    ]
    for month, count in r.monthly_totals.items():
        lines.append(f"| {month} | {count:,} |")

    lines += [
        "",
        "## Top 10 LSOAs",
        "",
        "| LSOA | Incidents |",
        "|---|---:|",
    ]
    for lsoa, count in r.top_lsoas.items():
        lines.append(f"| {lsoa} | {count:,} |")

    lines += [
        "",
        "## Key Findings",
        "",
        f"- Most common crime type: **{r.crime_type_counts.index[0]}** "
        f"({r.crime_type_counts.iloc[0]:,} incidents)",
        f"- Busiest LSOA: **{r.top_lsoas.index[0]}** ({r.top_lsoas.iloc[0]:,} incidents)",
        f"- Monthly range: {r.monthly_totals.min():,} – {r.monthly_totals.max():,}",
        f"- Most common location string: **{r.location_top.index[0]}** "
        f"({r.location_top.iloc[0]:,} incidents)",
        "",
        "## Figures",
        "",
        "See `outputs/figures/` for all visualizations.",
        "",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Wrote EDA report: {out_path.relative_to(config.paths.project_root)}")



def generate_hypothesis_report(df: pd.DataFrame, out_path: Path) -> None:
    results = run_hypotheses(df)
    lines = ["# Hypothesis Testing Report", ""]
    for r in results:
        lines += [
            f"## {r.name}",
            f"- **Statistic:** {r.statistic:.4f}",
            f"- **p-value:** {r.p_value:.3e}",
            f"- **Conclusion:** {r.conclusion}",
            "",
        ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Wrote hypothesis report: {out_path.relative_to(config.paths.project_root)}")



def main() -> None:
    df = pd.read_parquet(config.paths.processed_data_dir / config.data["cleaned_filename"])
    generate_eda_report(df, config.paths.reports_dir / "eda_report.md")
    generate_hypothesis_report(df, config.paths.reports_dir / "hypothesis_report.md")


if __name__ == "__main__":
    main()