"""Check 4: Spojnosc - czy wartosci w kolumnie pasuja do jednego typu/formatu.

Dla kolumn tekstowych probujemy zgadnac dominujacy "wzorzec" (liczba, data,
e-mail, zwykly tekst) i liczymy, ile wartosci od niego odstaje. Np. kolumna
z wiekiem, w ktorej 98% to liczby, a 2% to "brak danych" - jest niespojna.
"""
from __future__ import annotations

import re

import pandas as pd

from app.checks.base import BaseCheck, text_columns
from app.models.schemas import CheckResult

_NUMBER_RE = re.compile(r"^-?\d+([.,]\d+)?$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_DATE_RE = re.compile(r"^\d{2,4}[-/.]\d{1,2}[-/.]\d{1,4}$")


def _classify(value: str) -> str:
    value = value.strip()
    if _EMAIL_RE.match(value):
        return "email"
    if _DATE_RE.match(value):
        return "date"
    if _NUMBER_RE.match(value):
        return "number"
    return "text"


class ConsistencyCheck(BaseCheck):
    name = "consistency"
    label = "Spojnosc typow / formatow"
    weight = 0.15

    def run(self, df: pd.DataFrame) -> CheckResult:
        text_cols = text_columns(df)
        if len(text_cols) == 0:
            return self._result(
                100.0, {"note": "Brak kolumn tekstowych do analizy."}, []
            )

        total_values = 0
        total_bad = 0
        per_col = {}
        issues = []
        for col in text_cols:
            series = df[col].dropna().astype(str)
            if series.empty:
                continue
            kinds = series.map(_classify)
            dominant = kinds.mode().iloc[0]
            bad = int((kinds != dominant).sum())
            total_values += len(series)
            total_bad += bad
            per_col[col] = {"dominant_format": dominant, "non_matching": bad}
            if bad > 0:
                issues.append(
                    f"Kolumna '{col}': {bad} wartosci nie pasuje do formatu '{dominant}'."
                )

        score = 100.0 if total_values == 0 else (1 - total_bad / total_values) * 100
        details = {"per_column": per_col}
        return self._result(score, details, issues)
