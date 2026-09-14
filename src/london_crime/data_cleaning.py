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