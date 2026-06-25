"""ReportBuilder - z jednego QualityReport robi rozne "widoki".

JSON dostajemy za darmo z Pydantic. HTML renderujemy szablonem Jinja2.
PDF powstaje z tego samego HTML przez WeasyPrint - dane liczymy raz.
"""
from __future__ import annotations

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


class ReportBuilder:
    def __init__(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader(str(_TEMPLATES_DIR)),
            autoescape=select_autoescape(["html"]),
        )

    def to_html(self, report: QualityReport) -> str:
        template = self.env.get_template("report.html")
        return template.render(
            report=report,
            grade_color=_GRADE_COLORS.get(report.grade, "#64748b"),
        )

    def to_pdf(self, report: QualityReport) -> bytes:
        """Renderuje HTML i konwertuje go do PDF (WeasyPrint)."""
        from weasyprint import HTML  # import lokalny - ciezka zaleznosc

        html = self.to_html(report)
        return HTML(string=html).write_pdf()
