"""Analyzer - orkiestrator. Jedyne miejsce, ktore wie, jakie checki istnieja.

Uruchamia po kolei wszystkie checki, zbiera ich wyniki, oddaje je do
ScoringEngine i sklada finalny QualityReport.
"""
from __future__ import annotations

import uuid

import pandas as pd

from app.checks.anomaly_ml import AnomalyMLCheck
from app.checks.completeness import CompletenessCheck
from app.checks.consistency import ConsistencyCheck
from app.checks.constant import ConstantColumnsCheck
from app.checks.outliers import OutliersCheck
from app.checks.uniqueness import UniquenessCheck
from app.checks.validity import ValidityCheck
from app.checks.whitespace import WhitespaceCheck
from app.core.scoring import ScoringEngine
from app.models.schemas import CheckResult, DatasetInfo, QualityReport


class Analyzer:
    def __init__(self) -> None:
        # Rejestr checkow. Dodanie nowego = dopisanie jednej linijki tutaj.
        self.checks = [
            CompletenessCheck(),
            UniquenessCheck(),
            OutliersCheck(),
            ConsistencyCheck(),
            ValidityCheck(),
            WhitespaceCheck(),
            ConstantColumnsCheck(),
            AnomalyMLCheck(),
        ]
        self.scoring = ScoringEngine()

    def analyze(self, df: pd.DataFrame) -> QualityReport:
        results: list[CheckResult] = []
        for check in self.checks:
            try:
                results.append(check.run(df))
            except Exception as exc:  # noqa: BLE001 - pojedynczy check nie moze wywalic calosci
                results.append(
                    CheckResult(
                        name=check.name,
                        label=check.label,
                        score=0.0,
                        weight=check.weight,
                        passed=False,
                        details={"error": str(exc)},
                        issues=[f"Check '{check.label}' nie powiodl sie: {exc}"],
                    )
                )

        overall = self.scoring.overall_score(results)
        grade = self.scoring.grade_for(overall)
        suggestions = self.scoring.build_suggestions(results)

        return QualityReport(
            report_id=uuid.uuid4().hex[:8],
            dataset=DatasetInfo(
                rows=int(df.shape[0]),
                columns=int(df.shape[1]),
                column_names=list(df.columns.astype(str)),
            ),
            overall_score=overall,
            grade=grade,
            checks=results,
            suggestions=suggestions,
        )
