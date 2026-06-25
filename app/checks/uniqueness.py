"""Check 2: Unikalnosc - ile zduplikowanych (identycznych) wierszy."""
from __future__ import annotations

import pandas as pd

from app.checks.base import BaseCheck
from app.models.schemas import CheckResult


class UniquenessCheck(BaseCheck):
    name = "uniqueness"
    label = "Unikalnosc (duplikaty wierszy)"
    weight = 0.15

    def run(self, df: pd.DataFrame) -> CheckResult:
        n = len(df)
        duplicates = int(df.duplicated().sum())
        score = 100.0 if n == 0 else (1 - duplicates / n) * 100

        issues = []
        if duplicates > 0:
            issues.append(f"Wykryto {duplicates} zduplikowanych wierszy.")
        details = {"duplicate_rows": duplicates, "total_rows": n}
        return self._result(score, details, issues)
