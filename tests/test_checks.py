"""Testy jednostkowe checkow - kazdy na malej, recznie spreparowanej ramce."""
import pandas as pd

from app.checks.completeness import CompletenessCheck
from app.checks.uniqueness import UniquenessCheck
from app.checks.outliers import OutliersCheck
from app.checks.constant import ConstantColumnsCheck
from app.checks.whitespace import WhitespaceCheck


def test_completeness_detects_missing():
    df = pd.DataFrame({"a": [1, None], "b": [1, 2]})  # 1 z 4 komorek pusta
    result = CompletenessCheck().run(df)
    assert result.score == 75.0
    assert result.issues  # powinna byc uwaga o brakach


def test_completeness_perfect():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    assert CompletenessCheck().run(df).score == 100.0


def test_uniqueness_detects_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})  # 1 duplikat
    result = UniquenessCheck().run(df)
    assert result.details["duplicate_rows"] == 1


def test_outliers_flags_extreme_value():
    df = pd.DataFrame({"x": [10, 11, 12, 13, 1000]})  # 1000 to outlier
    result = OutliersCheck().run(df)
    assert result.details["total_outliers"] >= 1


def test_constant_column_detected():
    df = pd.DataFrame({"const": [5, 5, 5], "var": [1, 2, 3]})
    result = ConstantColumnsCheck().run(df)
    assert "const" in result.details["constant_columns"]


def test_whitespace_detected():
    df = pd.DataFrame({"city": [" Gdansk ", "Gdansk", "Warszawa"]})
    result = WhitespaceCheck().run(df)
    assert result.score < 100.0
