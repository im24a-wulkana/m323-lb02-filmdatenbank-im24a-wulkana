"""Statistiken über den Filmkatalog."""

from dataclasses import dataclass
from functools import partial, reduce
from itertools import starmap

from app.catalog import average_rating
from app.functional import pipe


@dataclass(frozen=True)
class GroupStats:
    """Kennzahlen einer Gruppe von Filmen, z.B. eines Genres."""
    name: str
    count: int
    average_rating: float
    total_runtime: int
    best_title: str


@dataclass(frozen=True)
class Overview:
    """Kennzahlen über den ganzen Katalog."""
    count: int
    average_rating: float | None
    total_runtime: int


def movie_genres(movie):
    """Liefert die Gruppenschlüssel eines Films nach Genre."""
    return movie.genres


def movie_decade(movie):
    """Liefert den Gruppenschlüssel eines Films nach Jahrzehnt, z.B. "1990er"."""
    return (f"{movie.year // 10 * 10}er",)


def movie_director(movie):
    """Liefert den Gruppenschlüssel eines Films nach Regie."""
    return (movie.director,)


def add_to_group(groups, pair):
    """
    Fügt einen Film zu seiner Gruppe hinzu, ohne die bisherigen Gruppen zu verändern.

    Args:
        groups (dict[str, tuple[Movie, ...]]): Die bisherigen Gruppen.
        pair (tuple[str, Movie]): Der Gruppenschlüssel und der Film.

    Returns:
        dict[str, tuple[Movie, ...]]: Ein neues Dictionary mit dem Film in seiner Gruppe.
    """
    key, movie = pair
    return {**groups, key: (*groups.get(key, ()), movie)}


def group_by(movies, keys_of):
    """
    Gruppiert Filme. Ein Film kann in mehreren Gruppen vorkommen.

    Args:
        movies (Iterable[Movie]): Die Filme.
        keys_of (Callable[[Movie], Iterable[str]]): Liefert die Gruppen eines Films.

    Returns:
        dict[str, tuple[Movie, ...]]: Die Filme pro Gruppe in ursprünglicher Reihenfolge.
    """
    pairs = ((key, movie) for movie in movies for key in keys_of(movie))
    return reduce(add_to_group, pairs, {})


def summarize_group(name, movies):
    """
    Berechnet die Kennzahlen einer Gruppe.

    Args:
        name (str): Der Name der Gruppe.
        movies (tuple[Movie, ...]): Die Filme der Gruppe, mindestens einer.

    Returns:
        GroupStats: Die Kennzahlen der Gruppe.
    """
    rating_sum = reduce(lambda total, movie: total + movie.rating, movies, 0.0)
    return GroupStats(
        name=name,
        count=len(movies),
        average_rating=round(rating_sum / len(movies), 2),
        total_runtime=reduce(lambda total, movie: total + movie.runtime, movies, 0),
        best_title=max(movies, key=lambda movie: movie.rating).title,
    )


def summarize_groups(groups):
    """Berechnet die Kennzahlen aller Gruppen."""
    return tuple(starmap(summarize_group, groups.items()))


def by_count(stats):
    """Sortierschlüssel: meiste Filme zuerst, dann beste Bewertung, dann Name."""
    return (-stats.count, -stats.average_rating, stats.name.casefold())


def by_average(stats):
    """Sortierschlüssel: beste Bewertung zuerst, dann meiste Filme, dann Name."""
    return (-stats.average_rating, -stats.count, stats.name.casefold())


def by_runtime(stats):
    """Sortierschlüssel: längste Gesamtlaufzeit zuerst, dann Name."""
    return (-stats.total_runtime, stats.name.casefold())


def by_name(stats):
    """Sortierschlüssel: alphabetisch nach Name."""
    return stats.name.casefold()


GROUP_SORTS = {
    "count": by_count,
    "average": by_average,
    "runtime": by_runtime,
    "name": by_name,
}


def group_report(movies, keys_of, sort_key, min_count=1):
    """
    Erstellt einen sortierten Bericht über Gruppen von Filmen.

    Args:
        movies (Iterable[Movie]): Die Filme.
        keys_of (Callable[[Movie], Iterable[str]]): Liefert die Gruppen eines Films.
        sort_key (Callable[[GroupStats], Any]): Der Sortierschlüssel für die Gruppen.
        min_count (int): Gruppen mit weniger Filmen werden weggelassen.

    Returns:
        tuple[GroupStats, ...]: Die Kennzahlen der Gruppen in sortierter Reihenfolge.
    """
    return pipe(
        partial(group_by, keys_of=keys_of),
        summarize_groups,
        partial(filter, lambda stats: stats.count >= min_count),
        partial(sorted, key=sort_key),
        tuple,
    )(movies)


def genre_report(movies, sort="count"):
    """Kennzahlen pro Genre, sortiert nach dem gewählten Kriterium."""
    return group_report(movies, movie_genres, GROUP_SORTS.get(sort, by_count))


def decade_report(movies):
    """Kennzahlen pro Jahrzehnt in chronologischer Reihenfolge."""
    return group_report(movies, movie_decade, by_name)


def director_report(movies, min_count=2):
    """Regie mit mindestens min_count Filmen, die beste Bewertung zuerst."""
    return group_report(movies, movie_director, by_average, min_count)


def overview(movies):
    """
    Berechnet die Kennzahlen des ganzen Katalogs.

    Args:
        movies (Sequence[Movie]): Die Filme.

    Returns:
        Overview: Anzahl, Durchschnittsbewertung und Gesamtlaufzeit.
    """
    return Overview(
        count=len(movies),
        average_rating=average_rating(movies),
        total_runtime=reduce(lambda total, movie: total + movie.runtime, movies, 0),
    )
