"""Check 6: Biale znaki i wielkosc liter - ciche zrodlo bledow w danych.

Wykrywa wartosci z nadmiarowymi spacjami (' Tak' vs 'Tak') oraz przypadki,
gdy ta sama wartosc wystepuje w roznej wielkosci liter ('Yes' i 'yes'),
co psuje grupowanie i liczenie unikalnych wartosci.
"""
from __future__ import annotations

import pandas as pd

from app.checks.base import BaseCheck
from app.models.schemas import CheckResult


class WhitespaceCheck(BaseCheck):
    name = "whitespace"
    label = "Biale znaki / wielkosc liter"
    weight = 0.10

    def run(self, df: pd.DataFrame) -> CheckResult:
        text_cols = df.select_dtypes(include="object").columns
        if len(text_cols) == 0:
            return self._result(100.0, {"note": "Brak kolumn tekstowych."}, [])

        total_values = 0
        total_dirty = 0
        issues = []
        per_col = {}
        for col in text_cols:
            series = df[col].dropna().astype(str)
            if series.empty:
                continue
            ws = int((series != series.str.strip()).sum())

            # Niespojna wielkosc liter: ta sama wartosc po normalizacji,
            # ale rozna w oryginale.
            normalized = series.str.strip().str.lower()
            casing_groups = series.groupby(normalized).nunique()
            casing_issues = int((casing_groups > 1).sum())

            dirty = ws  # do score liczymy spacje (najpewniejszy sygnal)
            total_values += len(series)
            total_dirty += dirty
            per_col[col] = {"whitespace_values": ws, "casing_variants": casing_issues}
            if ws > 0:
                issues.append(f"Kolumna '{col}': {ws} wartosci z nadmiarowymi spacjami.")
            if casing_issues > 0:
                issues.append(
                    f"Kolumna '{col}': {casing_issues} wartosci z niespojna wielkoscia liter."
                )

        score = 100.0 if total_values == 0 else (1 - total_dirty / total_values) * 100
        return self._result(score, {"per_column": per_col}, issues)
