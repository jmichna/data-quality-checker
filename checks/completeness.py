"""Check 1: Kompletnosc - ile brakujacych wartosci (NaN) jest w danych."""
from __future__ import annotations

import pandas as pd

from app.checks.base import BaseCheck
from app.models.schemas import CheckResult


class CompletenessCheck(BaseCheck):
    name = "completeness"
    label = "Kompletnosc (braki danych)"
    weight = 0.20

    def run(self, df: pd.DataFrame) -> CheckResult:
        total_cells = int(df.size)
        missing = int(df.isna().sum().sum())
        score = 100.0 if total_cells == 0 else (1 - missing / total_cells) * 100

        per_col = (df.isna().mean() * 100).round(2)
        issues = [
            f"Kolumna '{col}' ma {pct}% brakow"
            for col, pct in per_col.items()
            if pct > 0
        ]
        details = {
            "missing_cells": missing,
            "total_cells": total_cells,
            "per_column_pct": per_col.to_dict(),
        }
        return self._result(score, details, issues)
