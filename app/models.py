"""Datenmodell der Filmdatenbank."""

from dataclasses import dataclass, replace

MIN_YEAR = 1888
MAX_YEAR = 2100
MAX_RATING = 10.0


@dataclass(frozen=True)
class Movie:
    """Ein unveränderlicher Film."""
    title: str
    year: int
    genres: tuple[str, ...]
    director: str
    runtime: int
    rating: float


def movie_key(movie):
    """
    Liefert den Schlüssel, der einen Film eindeutig bestimmt.

    Args:
        movie (Movie): Der Film.

    Returns:
        tuple[str, int]: Der Titel ohne Grossschreibung und das Jahr.
    """
    return movie.title.casefold(), movie.year


def with_rating(movie, rating):
    """
    Liefert eine Kopie des Films mit neuer Bewertung.

    Args:
        movie (Movie): Der ursprüngliche Film, er bleibt unverändert.
        rating (float): Die neue Bewertung.

    Returns:
        Movie: Ein neuer Film mit allen anderen Feldern des Originals.
    """
    return replace(movie, rating=rating)


def parse_text(value):
    """
    Liest einen Pflichttext.

    Args:
        value (str | None): Der Rohwert aus der CSV-Datei.

    Returns:
        str: Der Text ohne umgebende Leerzeichen.

    Raises:
        ValueError: Wenn der Text leer ist oder fehlt.
    """
    text = (value or "").strip()
    if not text:
        raise ValueError("Pflichtfeld ist leer")
    return text


def parse_number(value, convert, minimum, maximum):
    """
    Liest eine Zahl und prüft ihren Wertebereich.

    Args:
        value (str | None): Der Rohwert aus der CSV-Datei.
        convert (callable): Die Umwandlungsfunktion, z.B. int oder float.
        minimum (int | float): Der kleinste erlaubte Wert.
        maximum (int | float): Der grösste erlaubte Wert.

    Returns:
        int | float: Die umgewandelte Zahl.

    Raises:
        ValueError: Wenn der Wert keine Zahl ist oder ausserhalb des Bereichs liegt.
    """
    number = convert((value or "").strip())
    if not minimum <= number <= maximum:
        raise ValueError(f"{number} liegt nicht zwischen {minimum} und {maximum}")
    return number


def parse_year(value):
    """Liest ein Erscheinungsjahr."""
    return parse_number(value, int, MIN_YEAR, MAX_YEAR)


def parse_runtime(value):
    """Liest eine Laufzeit in Minuten."""
    return parse_number(value, int, 1, 24 * 60)


def parse_rating(value):
    """Liest eine Bewertung von 0 bis 10."""
    return parse_number(value, float, 0.0, MAX_RATING)


def parse_genres(value):
    """
    Liest die mit | getrennten Genres.

    Args:
        value (str | None): Der Rohwert, z.B. "Drama|Krimi".

    Returns:
        tuple[str, ...]: Die Genres ohne leere Einträge.

    Raises:
        ValueError: Wenn kein Genre angegeben ist.
    """
    genres = tuple(filter(None, map(str.strip, (value or "").split("|"))))
    if not genres:
        raise ValueError("Mindestens ein Genre ist nötig")
    return genres


FIELD_PARSERS = {
    "title": parse_text,
    "year": parse_year,
    "genres": parse_genres,
    "director": parse_text,
    "runtime": parse_runtime,
    "rating": parse_rating,
}


def movie_from_row(row):
    """
    Erstellt einen Film aus einer CSV-Zeile.

    Args:
        row (dict): Die Zeile mit den Spaltennamen als Schlüssel.

    Returns:
        Movie: Der validierte Film.

    Raises:
        ValueError: Wenn die Zeile zu viele Spalten hat oder ein Feld ungültig ist.
    """
    if None in row:
        raise ValueError("Zeile hat zu viele Spalten")
    return Movie(**{field: parse(row.get(field)) for field, parse in FIELD_PARSERS.items()})
