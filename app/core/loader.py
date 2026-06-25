"""DataLoader - wczytywanie pliku CSV do pandas.DataFrame.

Odpowiada wyłącznie za bezpieczne wczytanie danych: wykrycie separatora,
poradzenie sobie z kodowaniem i sensowne błędy, gdy plik jest zepsuty.
"""
from __future__ import annotations

import io

import pandas as pd


class DataLoadError(Exception):
    """Rzucany, gdy pliku nie da się wczytać jako poprawnego CSV."""


def load_csv(source: str | bytes | io.BytesIO) -> pd.DataFrame:
    """Wczytuje CSV ze ścieżki, bajtów lub strumienia.

    sep=None + engine='python' sprawia, że pandas sam wykrywa separator
    (przecinek, średnik, tab). Najpierw próbujemy UTF-8, a gdy padnie -
    latin-1, bo polskie pliki bywają w roznych kodowaniach.
    """
    if isinstance(source, bytes):
        source = io.BytesIO(source)

    for encoding in ("utf-8", "latin-1"):
        try:
            if isinstance(source, io.BytesIO):
                source.seek(0)
            df = pd.read_csv(source, sep=None, engine="python", encoding=encoding)
            if df.shape[1] == 0:
                raise DataLoadError("Plik nie zawiera zadnych kolumn.")
            if df.empty:
                raise DataLoadError("Plik CSV jest pusty (brak wierszy).")
            return df
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError as exc:
            raise DataLoadError("Plik CSV jest pusty.") from exc
        except Exception as exc:  # noqa: BLE001
            raise DataLoadError(f"Nie udalo sie wczytac CSV: {exc}") from exc

    raise DataLoadError("Nie udalo sie rozpoznac kodowania pliku.")
