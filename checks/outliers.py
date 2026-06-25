"""Check 3: Outliery - wartosci odstajace w kolumnach numerycznych.

Metoda IQR (rozstep miedzykwartylowy): wartosc jest outlierem, gdy lezy
ponizej Q1 - 1.5*IQR albo powyzej Q3 + 1.5*IQR. To klasyczna, odporna
statystycznie metoda (ta sama, ktorej uzywa wykres pudelkowy / boxplot).
"""
from __future__ import annotations

import pandas as pd

from app.checks.base import BaseCheck
from app.models.schemas import CheckResult


class OutliersCheck(BaseCheck):
    name = "outliers"
    label = "Wartosci odstajace (outliery)"
    weight = 0.15

    def run(self, df: pd.DataFrame) -> CheckResult:
        numeric = df.select_dtypes(include="number")
        if numeric.shape[1] == 0:
            return self._result(
                100.0, {"note": "Brak kolumn numerycznych do analizy."}, []
            )

        total_values = 0
        total_outliers = 0
        per_col = {}
        issues = []
        for col in numeric.columns:
            series = numeric[col].dropna()
            if series.empty:
                continue
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            mask = (series < low) | (series > high)
            count = int(mask.sum())
            per_col[col] = count
            total_values += len(series)
            total_outliers += count
            if count > 0:
                issues.append(f"Kolumna '{col}': {count} wartosci odstajacych.")

        score = 100.0 if total_values == 0 else (1 - total_outliers / total_values) * 100
        details = {"outliers_per_column": per_col, "total_outliers": total_outliers}
        return self._result(score, details, issues)
