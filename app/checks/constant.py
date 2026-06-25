"""Check 7: Kolumny stale - jedna wartosc w calej kolumnie.

Taka kolumna nie niesie informacji i jest bezuzyteczna dla modeli ML
(zerowa wariancja). Warto ja wykryc i zasugerowac usuniecie.
"""
from __future__ import annotations

import pandas as pd

from app.checks.base import BaseCheck
from app.models.schemas import CheckResult


class ConstantColumnsCheck(BaseCheck):
    name = "constant_columns"
    label = "Kolumny stale (zerowa wariancja)"
    weight = 0.05

    def run(self, df: pd.DataFrame) -> CheckResult:
        n_cols = df.shape[1]
        if n_cols == 0:
            return self._result(100.0, {"note": "Brak kolumn."}, [])

        constant = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]
        score = (1 - len(constant) / n_cols) * 100
        issues = [f"Kolumna '{c}' ma tylko jedna wartosc (stala)." for c in constant]
        details = {"constant_columns": constant}
        return self._result(score, details, issues)
