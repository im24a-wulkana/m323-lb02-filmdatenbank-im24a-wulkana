"""Suche, Filter und Sortierung des Filmkatalogs."""

import math
from dataclasses import dataclass
from functools import reduce
from itertools import chain

from app.models import movie_key

SORT_OPTIONS = (
    ("rating", "Bewertung"),
    ("year", "Jahr"),
    ("title", "Titel"),
    ("runtime", "Laufzeit"),
)

SORT_KEYS = {
    "rating": lambda movie: movie.rating,
    "year": lambda movie: movie.year,
    "title": lambda movie: movie.title.casefold(),
    "runtime": lambda movie: movie.runtime,
}

DEFAULT_SORT = "rating"


@dataclass(frozen=True)
class CatalogQuery:
    """Die Such- und Sortierwünsche für den Katalog."""
    text: str = ""
    genre: str = ""
    min_rating: float | None = None
    sort: str = DEFAULT_SORT
    descending: bool = True


def parse_optional_float(value):
    """
    Liest eine optionale endliche Zahl.

    Args:
        value (str | None): Der Rohwert aus der Anfrage.

    Returns:
        float | None: Die Zahl oder None, wenn der Wert fehlt oder ungültig ist.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def query_from_args(args):
    """
    Erstellt eine CatalogQuery aus den Parametern einer Anfrage.

    Args:
        args (Mapping[str, str]): Die Query-Parameter, z.B. request.args.

    Returns:
        CatalogQuery: Die bereinigte Anfrage mit gültiger Sortierung.
    """
    sort = args.get("sort", DEFAULT_SORT)
    return CatalogQuery(
        text=args.get("q", "").strip().casefold(),
        genre=args.get("genre", ""),
        min_rating=parse_optional_float(args.get("min_rating")),
        sort=sort if sort in SORT_KEYS else DEFAULT_SORT,
        descending=args.get("order", "desc") != "asc",
    )


def text_filter(text):
    """Liefert einen Filter für Titel oder Regie, ohne Grossschreibung zu beachten."""
    return lambda movie: text in movie.title.casefold() or text in movie.director.casefold()


def genre_filter(genre):
    """Liefert einen Filter für ein Genre."""
    return lambda movie: genre in movie.genres


def rating_filter(min_rating):
    """Liefert einen Filter für eine Mindestbewertung inklusive Grenzwert."""
    return lambda movie: movie.rating >= min_rating


def active_filters(query):
    """
    Erstellt die Filter, die für eine Anfrage aktiv sind.

    Args:
        query (CatalogQuery): Die Anfrage.

    Returns:
        tuple[Callable[[Movie], bool], ...]: Ein Filter pro gesetztem Kriterium.
    """
    candidates = (
        (query.text, text_filter),
        (query.genre, genre_filter),
        (query.min_rating, rating_filter),
    )
    return tuple(make_filter(value) for value, make_filter in candidates if value not in ("", None))


def search_catalog(movies, query):
    """
    Filtert und sortiert Filme gemäss einer Anfrage.

    Args:
        movies (Iterable[Movie]): Alle Filme.
        query (CatalogQuery): Die Anfrage.

    Returns:
        tuple[Movie, ...]: Die passenden Filme in der gewünschten Reihenfolge.
    """
    filters = active_filters(query)
    found = filter(lambda movie: all(check(movie) for check in filters), movies)
    return tuple(sorted(found, key=SORT_KEYS[query.sort], reverse=query.descending))


def average_rating(movies):
    """
    Berechnet die durchschnittliche Bewertung.

    Args:
        movies (Sequence[Movie]): Die Filme.

    Returns:
        float | None: Der auf eine Stelle gerundete Durchschnitt oder None ohne Filme.
    """
    if not movies:
        return None
    ratings = map(lambda movie: movie.rating, movies)
    total = reduce(lambda subtotal, rating: subtotal + rating, ratings, 0.0)
    return round(total / len(movies), 1)


def make_lookup(movies):
    """
    Erstellt eine Suchfunktion für einzelne Filme.

    Args:
        movies (Sequence[Movie]): Die Filme, in denen gesucht wird.

    Returns:
        Callable[[str, int], Movie | None]: Liefert zu Titel und Jahr den ersten
        passenden Film oder None. Die Grossschreibung des Titels zählt nicht.
    """
    index = {movie_key(movie): movie for movie in reversed(movies)}

    def lookup(title, year):
        return index.get((title.casefold(), year))

    return lookup


def replace_movie(movies, updated):
    """
    Ersetzt einen Film durch eine neue Version.

    Args:
        movies (Iterable[Movie]): Die Filme.
        updated (Movie): Die neue Version, gefunden über Titel und Jahr.

    Returns:
        tuple[Movie, ...]: Ein neues Tupel, alle anderen Filme sind dieselben Objekte.
    """
    key = movie_key(updated)
    return tuple(map(lambda movie: updated if movie_key(movie) == key else movie, movies))


def all_genres(movies):
    """
    Liefert alle vorkommenden Genres.

    Args:
        movies (Iterable[Movie]): Die Filme.

    Returns:
        tuple[str, ...]: Jedes Genre einmal, alphabetisch sortiert.
    """
    return tuple(sorted(set(chain.from_iterable(map(lambda movie: movie.genres, movies)))))
