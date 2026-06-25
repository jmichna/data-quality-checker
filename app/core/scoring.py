"""ScoringEngine - zamienia liste wynikow checkow w jedna ocene koncowa.

Logika: srednia wazona ocen czastkowych -> wynik 0-100 -> litera A-F.
Dodatkowo buduje liste sugestii czyszczenia na podstawie 'issues' z checkow.
"""
from __future__ import annotations

from app.models.schemas import CheckResult

# Progi ocen literowych (gorna granica wlacznie liczona od dolu).
_GRADE_THRESHOLDS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]


class ScoringEngine:
    def grade_for(self, score: float) -> str:
        for threshold, letter in _GRADE_THRESHOLDS:
            if score >= threshold:
                return letter
        return "F"

    def overall_score(self, checks: list[CheckResult]) -> float:
        total_weight = sum(c.weight for c in checks)
        if total_weight == 0:
            return 0.0
        weighted = sum(c.score * c.weight for c in checks)
        return round(weighted / total_weight, 2)

    def build_suggestions(self, checks: list[CheckResult], limit: int = 10) -> list[str]:
        """Sugestie naprawcze - bierzemy najpierw checki z najnizszym score."""
        suggestions: list[str] = []
        for check in sorted(checks, key=lambda c: c.score):
            for issue in check.issues:
                suggestions.append(issue)
                if len(suggestions) >= limit:
                    return suggestions
        if not suggestions:
            suggestions.append("Nie wykryto istotnych problemow z jakoscia danych.")
        return suggestions
