"""Export von Filmen als CSV."""

import csv
import io

FIELD_FORMATTERS = {
    "title": str,
    "year": str,
    "genres": "|".join,
    "director": str,
    "runtime": str,
    "rating": str,
}


def movie_to_row(movie):
    """
    Wandelt einen Film in eine CSV-Zeile um.

    Args:
        movie (Movie): Der Film.

    Returns:
        dict[str, str]: Die Zeile mit den Spaltennamen als Schlüssel.
    """
    return {
        field: format_value(getattr(movie, field))
        for field, format_value in FIELD_FORMATTERS.items()
    }


def export_movies(movies):
    """
    Exportiert Filme als CSV-Text im selben Format wie data/movies.csv.

    Args:
        movies (Iterable[Movie]): Die Filme.

    Returns:
        str: Der CSV-Text mit Kopfzeile.
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=tuple(FIELD_FORMATTERS), lineterminator="\n")
    writer.writeheader()
    writer.writerows(map(movie_to_row, movies))
    return buffer.getvalue()
