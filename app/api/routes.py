"""Warstwa REST API (FastAPI). Cienka - tylko HTTP, walidacja, bledy.

Cala logika jakosci siedzi w Analyzer. Tutaj odbieramy plik, wolamy analize
i zwracamy wynik w zadanym formacie. Raporty trzymamy w pamieci (prosty dict),
co w zupelnosci wystarcza na projekt zaliczeniowy.
"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response

from app.core.analyzer import Analyzer
from app.core.loader import DataLoadError, load_csv
from app.models.schemas import QualityReport
from app.report.builder import ReportBuilder

router = APIRouter()
_analyzer = Analyzer()
_builder = ReportBuilder()

# Prosty magazyn raportow w pamieci: report_id -> QualityReport
_REPORTS: dict[str, QualityReport] = {}


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Sprawdzenie, czy serwis zyje."""
    return {"status": "ok"}


@router.post("/analyze", response_model=QualityReport, tags=["analiza"])
async def analyze(file: UploadFile = File(...)) -> QualityReport:
    """Przyjmuje plik CSV, zwraca pelny raport jakosci (JSON)."""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Wymagany plik .csv")

    content = await file.read()
    try:
        df = load_csv(content)
    except DataLoadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    report = _analyzer.analyze(df)
    _REPORTS[report.report_id] = report
    return report


@router.get("/report/{report_id}", response_model=QualityReport, tags=["raport"])
def get_report(report_id: str) -> QualityReport:
    report = _REPORTS.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono raportu")
    return report


@router.get("/report/{report_id}/html", response_class=HTMLResponse, tags=["raport"])
def get_report_html(report_id: str) -> HTMLResponse:
    report = _REPORTS.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono raportu")
    return HTMLResponse(_builder.to_html(report))


@router.get("/report/{report_id}/pdf", tags=["raport"])
def get_report_pdf(report_id: str) -> Response:
    report = _REPORTS.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono raportu")
    pdf_bytes = _builder.to_pdf(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=raport_{report_id}.pdf"},
    )
