"""Modele danych (Pydantic) - to "kontrakty", jakie krążą po całej aplikacji.

W C# byłyby to klasy DTO z atrybutami walidacji. Pydantic robi to samo:
opisujemy kształt danych raz, a FastAPI automatycznie waliduje i serializuje
je do/z JSON-a.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CheckResult(BaseModel):
    """Wynik pojedynczego checka jakości. Każdy check zwraca dokładnie to."""

    name: str = Field(..., description="Techniczna nazwa, np. 'completeness'")
    label: str = Field(..., description="Czytelna nazwa do wyświetlenia")
    score: float = Field(..., ge=0, le=100, description="Ocena 0-100")
    weight: float = Field(..., ge=0, description="Waga w wyniku końcowym")
    passed: bool = Field(..., description="Czy check przeszedł próg")
    details: dict[str, Any] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list, description="Czytelne uwagi")


class DatasetInfo(BaseModel):
    """Podstawowe metadane wczytanego zbioru."""

    rows: int
    columns: int
    column_names: list[str]


class QualityReport(BaseModel):
    """Pełny raport jakości - finalny produkt analizy."""

    report_id: str
    dataset: DatasetInfo
    overall_score: float = Field(..., ge=0, le=100)
    grade: str
    checks: list[CheckResult]
    suggestions: list[str]
