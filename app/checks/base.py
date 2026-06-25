"""BaseCheck - wspolny interfejs dla wszystkich checkow jakosci.

To odpowiednik klasy abstrakcyjnej / interfejsu w C#. Kazdy konkretny check
dziedziczy po BaseCheck i implementuje run(df). Dzieki temu Analyzer moze
traktowac wszystkie checki jednakowo (polimorfizm).
"""
from __future__ import annotations

import warnings
from abc import ABC, abstractmethod

import pandas as pd

from app.models.schemas import CheckResult


def text_columns(df: pd.DataFrame) -> pd.Index:
    """Zwraca nazwy kolumn tekstowych, odpornie na rozne wersje pandas.

    W pandas 3 `select_dtypes(include="object")` ostrzega, ze domyslnie lapie
    tez nowy typ 'str'. Najpierw jawnie prosimy o oba typy (to wycisza ostrzezenie
    na nowym pandas). Starszy pandas nie zna tokena "str" i rzuca wyjatek -
    wtedy wracamy do "object", tlumiac samo ostrzezenie deprecjacyjne.
    """
    try:
        return df.select_dtypes(include=["object", "str"]).columns
    except (TypeError, ValueError):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return df.select_dtypes(include=["object"]).columns


class BaseCheck(ABC):
    name: str = "base"
    label: str = "Bazowy check"
    weight: float = 1.0
    threshold: float = 90.0  # ponizej tego score check uznajemy za "niezdany"

    @abstractmethod
    def run(self, df: pd.DataFrame) -> CheckResult:
        """Analizuje DataFrame i zwraca ustandaryzowany wynik."""

    def _result(self, score: float, details: dict, issues: list[str]) -> CheckResult:
        """Pomocnik budujacy CheckResult - skraca kod w kazdym checku."""
        score = round(max(0.0, min(100.0, score)), 2)
        return CheckResult(
            name=self.name,
            label=self.label,
            score=score,
            weight=self.weight,
            passed=score >= self.threshold,
            details=details,
            issues=issues,
        )
