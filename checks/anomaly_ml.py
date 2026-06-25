"""Check 8 (ML): Wykrywanie anomalii metoda Isolation Forest.

To rozszerzenie wpisujace sie w temat "sztuczna inteligencja". W odroznieniu
od pozostalych checkow (reguly), ten patrzy na WIELE kolumn naraz i znajduje
wiersze nietypowe wielowymiarowo - takie, ktorych zaden pojedynczy warunek
nie wychwyci. Isolation Forest izoluje obserwacje losowymi podzialami;
anomalie izoluja sie srednio szybciej niz punkty typowe.
"""
from __future__ import annotations

import pandas as pd

from app.checks.base import BaseCheck
from app.models.schemas import CheckResult


class AnomalyMLCheck(BaseCheck):
    name = "anomaly_ml"
    label = "Anomalie ML (Isolation Forest)"
    weight = 0.10
    threshold = 85.0

    def run(self, df: pd.DataFrame) -> CheckResult:
        # Import lokalnie, by reszta aplikacji dzialala nawet bez scikit-learn.
        from sklearn.ensemble import IsolationForest

        numeric = df.select_dtypes(include="number")
        if numeric.shape[1] == 0 or len(numeric) < 10:
            return self._result(
                100.0,
                {"note": "Za malo danych numerycznych do analizy ML (min. 10 wierszy)."},
                [],
            )

        # Model nie radzi sobie z NaN - uzupelniamy mediana kolumny.
        x = numeric.fillna(numeric.median(numeric_only=True))
        model = IsolationForest(contamination="auto", random_state=42)
        preds = model.fit_predict(x)  # -1 = anomalia, 1 = norma
        anomalies = int((preds == -1).sum())
        rate = anomalies / len(x)
        score = (1 - rate) * 100

        issues = []
        if anomalies > 0:
            issues.append(
                f"Model wykryl {anomalies} nietypowych wierszy ({round(rate*100,1)}%)."
            )
        details = {"anomalies": anomalies, "rows_analyzed": int(len(x))}
        return self._result(score, details, issues)
