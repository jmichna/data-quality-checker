"""Check 5: Poprawnosc zakresow (validity) - wartosci spoza sensownego zakresu.

Bez recznie podanych regul stosujemy heurystyki oparte o nazwy kolumn:
- kolumny typu wiek/age: wartosc musi byc w przedziale 0-120,
- kolumny typu cena/price/kwota/amount/ilosc/qty: nie moga byc ujemne,
- kolumny z procentami: 0-100.
To pokazuje pomysl "regul domenowych" - latwo go pozniej rozszerzyc.
"""
from __future__ import annotations

import pandas as pd

from app.checks.base import BaseCheck
from app.models.schemas import CheckResult

# Slowo-klucz w nazwie kolumny -> (min, max) dozwolony zakres
_RULES = {
    "age": (0, 120),
    "wiek": (0, 120),
    "price": (0, None),
    "cena": (0, None),
    "amount": (0, None),
    "kwota": (0, None),
    "qty": (0, None),
    "ilosc": (0, None),
    "count": (0, None),
    "percent": (0, 100),
    "procent": (0, 100),
}


def _rule_for(column: str):
    col = column.lower()
    for key, rng in _RULES.items():
        if key in col:
            return rng
    return None


class ValidityCheck(BaseCheck):
    name = "validity"
    label = "Poprawnosc zakresow wartosci"
    weight = 0.10

    def run(self, df: pd.DataFrame) -> CheckResult:
        total_checked = 0
        total_invalid = 0
        per_col = {}
        issues = []
        for col in df.columns:
            rule = _rule_for(col)
            if rule is None or not pd.api.types.is_numeric_dtype(df[col]):
                continue
            low, high = rule
            series = df[col].dropna()
            mask = pd.Series(False, index=series.index)
            if low is not None:
                mask |= series < low
            if high is not None:
                mask |= series > high
            invalid = int(mask.sum())
            total_checked += len(series)
            total_invalid += invalid
            per_col[col] = {"rule": [low, high], "invalid": invalid}
            if invalid > 0:
                issues.append(
                    f"Kolumna '{col}': {invalid} wartosci poza zakresem {low}-{high}."
                )

        if total_checked == 0:
            return self._result(
                100.0, {"note": "Brak kolumn pasujacych do regul zakresow."}, []
            )
        score = (1 - total_invalid / total_checked) * 100
        return self._result(score, {"per_column": per_col}, issues)
