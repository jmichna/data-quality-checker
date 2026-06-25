"""Punkt startowy aplikacji FastAPI.

Uruchomienie:  uvicorn app.main:app --reload
Dokumentacja Swagger:  http://127.0.0.1:8000/docs
Dashboard:  http://127.0.0.1:8000/
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes import router

app = FastAPI(
    title="Data Quality Checker",
    description="Analiza jakosci datasetu CSV: braki, duplikaty, outliery, spojnosc + scoring i raporty.",
    version="1.0.0",
)

# CORS - pozwala frontendowi (HTML+JS) wolac API takze spoza tego serwera.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

_UI_FILE = Path(__file__).resolve().parent.parent / "ui" / "index.html"


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    """Serwuje dashboard HTML+JS pod adresem glownym."""
    return FileResponse(_UI_FILE)
