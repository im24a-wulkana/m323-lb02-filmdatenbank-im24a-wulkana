"""Import von Filmen aus CSV-Daten."""

import csv
import io
from dataclasses import dataclass
from pathlib import Path

from app.models import Movie, movie_from_row, movie_key


@dataclass(frozen=True)
class RowError:
    """Eine CSV-Zeile, die nicht importiert werden konnte."""
    line: int
    message: str


@dataclass(frozen=True)
class ImportResult:
    """Das Ergebnis eines Imports."""
    movies: tuple[Movie, ...]
    errors: tuple[RowError, ...]
    duplicates: int


def read_rows(text):
    """
    Liest die Zeilen eines CSV-Textes.

    Args:
        text (str): Der Inhalt der CSV-Datei.

    Returns:
        tuple[tuple[int, dict], ...]: Die Zeilen mit ihrer Zeilennummer in der Datei.
    """
    reader = csv.DictReader(io.StringIO(text))
    return tuple((reader.line_num, row) for row in reader)


def parse_row(numbered_row):
    """
    Wandelt eine nummerierte Zeile in einen Film um.

    Args:
        numbered_row (tuple[int, dict]): Die Zeilennummer und die Zeile.

    Returns:
        Movie | RowError: Der Film oder der Fehler dieser Zeile.
    """
    line, row = numbered_row
    try:
        return movie_from_row(row)
    except ValueError as error:
        return RowError(line, str(error))


def is_movie(result):
    """Prüft, ob ein Ergebnis von parse_row ein Film ist."""
    return isinstance(result, Movie)


def is_error(result):
    """Prüft, ob ein Ergebnis von parse_row ein Fehler ist."""
    return isinstance(result, RowError)


def remove_duplicates(movies):
    """
    Entfernt doppelte Filme, das erste Vorkommen bleibt erhalten.

    Das Dictionary ist lokal und wird nur hier verändert. Von aussen bleibt die
    Funktion pure: gleiche Eingabe, gleiche Ausgabe, keine Nebeneffekte.

    Args:
        movies (Iterable[Movie]): Die Filme.

    Returns:
        tuple[Movie, ...]: Die Filme ohne Duplikate in der ursprünglichen Reihenfolge.
    """
    first_by_key = {}
    for movie in movies:
        first_by_key.setdefault(movie_key(movie), movie)
    return tuple(first_by_key.values())


def import_movies(text):
    """
    Importiert Filme aus einem CSV-Text.

    Args:
        text (str): Der Inhalt der CSV-Datei.

    Returns:
        ImportResult: Die eindeutigen Filme, die Fehler und die Anzahl Duplikate.
    """
    results = tuple(map(parse_row, read_rows(text)))
    valid_movies = tuple(filter(is_movie, results))
    unique_movies = remove_duplicates(valid_movies)
    return ImportResult(
        movies=unique_movies,
        errors=tuple(filter(is_error, results)),
        duplicates=len(valid_movies) - len(unique_movies),
    )


def import_summary(result):
    """
    Beschreibt ein Importergebnis in einem Satz.

    Args:
        result (ImportResult): Das Ergebnis des Imports.

    Returns:
        str: Die Zusammenfassung, z.B. "105 Filme importiert, 0 Duplikate entfernt, 0 Fehler".
    """
    return (f"{len(result.movies)} Filme importiert, {result.duplicates} Duplikate entfernt, "
            f"{len(result.errors)} Fehler")


def log_import(result, logger):
    """
    Schreibt ein Importergebnis ins Log.

    Args:
        result (ImportResult): Das Ergebnis des Imports.
        logger (logging.Logger): Das Log, in das geschrieben wird.
    """
    logger.info(import_summary(result))
    for error in result.errors:
        logger.warning("Zeile %s: %s", error.line, error.message)


def load_movies(path):
    """
    Importiert Filme aus einer CSV-Datei.

    Args:
        path (str | Path): Der Pfad zur CSV-Datei.

    Returns:
        ImportResult: Das Ergebnis des Imports.
    """
    return import_movies(Path(path).read_text(encoding="utf-8-sig"))
