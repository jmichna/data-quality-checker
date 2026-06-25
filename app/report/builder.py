"""ReportBuilder - z jednego QualityReport robi rozne "widoki".

JSON dostajemy za darmo z Pydantic. HTML renderujemy szablonem Jinja2 (ladny,
na ekran). PDF generujemy przez xhtml2pdf - czysto pythonowa biblioteka, ktora
NIE wymaga zadnych bibliotek systemowych (w odroznieniu od WeasyPrint, ktory
na Windowsie potrzebuje GTK/Pango). PDF korzysta z osobnego, uproszczonego
szablonu opartego o tabele, bo silnik PDF wspiera tylko podzbior CSS.
"""
from __future__ import annotations

import io
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models.schemas import QualityReport

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_GRADE_COLORS = {
    "A": "#16a34a",
    "B": "#65a30d",
    "C": "#ca8a04",
    "D": "#ea580c",
    "F": "#dc2626",
}


def _bar_color(score: float) -> str:
    if score >= 90:
        return "#16a34a"
    if score >= 70:
        return "#ca8a04"
    return "#dc2626"


def _bar_width(score: float) -> int:
    """Szerokosc paska w PDF jako liczba calkowita procent (min. 2, max. 100).

    Minimalna szerokosc chroni silnik PDF (reportlab) przed zerowa/ujemna
    szerokoscia komorki, ktora wywolywala blad geometrii tabeli.
    """
    return max(2, min(100, round(score)))


class ReportBuilder:
    def __init__(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader(str(_TEMPLATES_DIR)),
            autoescape=select_autoescape(["html"]),
        )
        # Filtry dostepne w szablonach: kolor i szerokosc paska.
        self.env.filters["bar_color"] = _bar_color
        self.env.filters["bar_width"] = _bar_width

    def _grade_color(self, report: QualityReport) -> str:
        return _GRADE_COLORS.get(report.grade, "#64748b")

    def to_html(self, report: QualityReport) -> str:
        """Ladny raport na ekran (przegladarka)."""
        template = self.env.get_template("report.html")
        return template.render(report=report, grade_color=self._grade_color(report))

    def to_pdf(self, report: QualityReport) -> bytes:
        """Raport PDF (xhtml2pdf). Zwraca bajty gotowego pliku PDF."""
        from xhtml2pdf import pisa  # import lokalny

        template = self.env.get_template("report_pdf.html")
        html = template.render(report=report, grade_color=self._grade_color(report))

        buffer = io.BytesIO()
        result = pisa.CreatePDF(src=html, dest=buffer, encoding="utf-8")
        if result.err:
            raise RuntimeError("Nie udalo sie wygenerowac PDF z szablonu HTML.")
        return buffer.getvalue()
