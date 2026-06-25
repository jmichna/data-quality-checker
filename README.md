# 🔎 Data Quality Checker

Usluga do analizy jakosci datasetu **CSV**: wykrywa braki, duplikaty, wartosci
odstajace i niespojnosci, wystawia ocene jakosci (0-100 + litera A-F) oraz
generuje raport (JSON / HTML / PDF). Zawiera **REST API (FastAPI)** i prosty
**dashboard webowy (HTML+JS)**.

> Projekt na przedmiot *Wybrane zagadnienia sztucznej inteligencji*.

## Funkcje

- **8 checkow jakosci** (wymog: min. 5):
  1. Kompletnosc (braki danych)
  2. Unikalnosc (duplikaty wierszy)
  3. Wartosci odstajace (outliery, metoda IQR)
  4. Spojnosc typow / formatow (regex: liczby, daty, e-maile)
  5. Poprawnosc zakresow (reguly domenowe, np. wiek 0-120)
  6. Biale znaki / wielkosc liter
  7. Kolumny stale (zerowa wariancja)
  8. **Anomalie ML** - Isolation Forest (scikit-learn)
- **Scoring**: srednia wazona ocen czastkowych + ocena literowa A-F + sugestie czyszczenia
- **REST API**: `/analyze`, `/report/{id}`, raporty HTML i PDF, Swagger pod `/docs`
- **Dashboard**: drag&drop CSV, animowany wskaznik wyniku, paski per-check

## Wymagania

Python 3.10+. Zaleznosci w `requirements.txt`.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

> **PDF** generowany jest przez `xhtml2pdf` - czysto pythonowa bibliotke, ktora
> NIE wymaga zadnych bibliotek systemowych. Dziala od razu po `pip install`.
> (Wczesniej uzywany WeasyPrint na Windowsie wymagal GTK/Pango - dlatego go zmieniono.)

## Uruchomienie

```bash
uvicorn app.main:app --reload
```

- Dashboard:  http://127.0.0.1:8000/
- Swagger (dokumentacja API):  http://127.0.0.1:8000/docs

Wgraj `data/sample.csv` (zawiera celowo wprowadzone problemy jakosci), aby
zobaczyc dzialanie.

## Przykladowe wywolanie API

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
     -F "file=@data/sample.csv"
```

## Testy

```bash
pytest -q
```

## Struktura projektu

```
app/
  main.py            # start FastAPI + serwowanie dashboardu
  api/routes.py      # endpointy REST
  core/
    loader.py        # wczytywanie CSV
    analyzer.py      # orkiestrator checkow
    scoring.py       # silnik oceny
  checks/            # 8 niezaleznych checkow jakosci
  models/schemas.py  # modele Pydantic
  report/            # generowanie HTML/PDF (Jinja2 + xhtml2pdf)
ui/index.html        # dashboard HTML+JS
tests/               # testy pytest
data/sample.csv      # przykladowy dataset
```

## Technologie

`pandas`, `FastAPI`, `json`, `scikit-learn`, `Jinja2`, `xhtml2pdf`, `pytest`.
