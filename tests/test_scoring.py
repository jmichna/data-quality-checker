"""Testy silnika scoringu - srednia wazona i ocena literowa."""
from app.core.scoring import ScoringEngine
from app.models.schemas import CheckResult


def _chk(name, score, weight):
    return CheckResult(name=name, label=name, score=score, weight=weight, passed=score >= 90)


def test_weighted_average():
    engine = ScoringEngine()
    checks = [_chk("a", 100, 1.0), _chk("b", 0, 1.0)]
    assert engine.overall_score(checks) == 50.0


def test_grade_mapping():
    engine = ScoringEngine()
    assert engine.grade_for(95) == "A"
    assert engine.grade_for(82) == "B"
    assert engine.grade_for(55) == "F"


def test_suggestions_when_clean():
    engine = ScoringEngine()
    checks = [_chk("a", 100, 1.0)]
    sugg = engine.build_suggestions(checks)
    assert len(sugg) == 1  # komunikat "brak problemow"
