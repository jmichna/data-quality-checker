"""Test integracyjny REST API - realny upload CSV do endpointu /analyze."""
import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze_endpoint():
    csv = b"a,b\n1,2\n1,2\n3,\n"  # duplikat + brak
    files = {"file": ("test.csv", io.BytesIO(csv), "text/csv")}
    resp = client.post("/analyze", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_score" in data
    assert data["grade"] in {"A", "B", "C", "D", "F"}
    assert len(data["checks"]) == 8


def test_analyze_rejects_non_csv():
    files = {"file": ("x.txt", io.BytesIO(b"hello"), "text/plain")}
    assert client.post("/analyze", files=files).status_code == 400
