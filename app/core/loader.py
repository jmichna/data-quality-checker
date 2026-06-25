#DataLoader - wczytywanie pliku CSV do pandas.DataFrame.

# Odpowiada wyłącznie za bezpieczne wczytanie danych: wykrycie separatora,
# poradzenie sobie z kodowaniem i sensowne błędy, gdy plik jest zepsuty.

from __future__ import annotations

import io

import pandas as pd


class DataLoadError(Exception):
    """Brak poprawnego pliku .CSV lub nieudane wczytanie danych."""


def load_csv(source: str | bytes | io.BytesIO) -> pd.DataFrame:

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
        except Exception as exc:
            raise DataLoadError(f"Nie udalo sie wczytac CSV: {exc}") from exc

    raise DataLoadError("Nie udalo sie rozpoznac kodowania pliku.")
