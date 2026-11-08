"""Empfehlungen ähnlicher Filme, umgesetzt nach docs/design-blatt.md."""

from dataclasses import dataclass
from functools import partial, reduce
from operator import add

from app.functional import pipe
from app.models import MAX_RATING, Movie, movie_key

GENRE_WEIGHT = 50
DIRECTOR_WEIGHT = 20
YEAR_WEIGHT = 15
YEAR_RANGE = 30
RATING_WEIGHT = 15
MIN_SCORE = 40
DEFAULT_LIMIT = 5


@dataclass(frozen=True)
class Recommendation:
    """Ein empfohlener Film mit seinem Ähnlichkeitswert von 0 bis 100."""
    movie: Movie
    score: float


def genre_similarity(base, candidate):
    """
    Teilwert für gemeinsame Genres (Jaccard-Index).

    Args:
        base (Movie): Der Ausgangsfilm.
        candidate (Movie): Der verglichene Film.

    Returns:
        float: 0 ohne gemeinsames Genre bis GENRE_WEIGHT bei identischen Genres.
    """
    base_genres = set(base.genres)
    candidate_genres = set(candidate.genres)
    shared = base_genres & candidate_genres
    combined = base_genres | candidate_genres
    return GENRE_WEIGHT * len(shared) / len(combined)


def director_bonus(base, candidate):
    """Teilwert für gleiche Regie: DIRECTOR_WEIGHT oder 0."""
    return float(DIRECTOR_WEIGHT) if base.director == candidate.director else 0.0


def year_proximity(base, candidate):
    """Teilwert für zeitliche Nähe: YEAR_WEIGHT bei gleichem Jahr, 0 ab YEAR_RANGE Jahren."""
    distance = abs(base.year - candidate.year)
    return YEAR_WEIGHT * max(0.0, 1 - distance / YEAR_RANGE)


def rating_bonus(_base, candidate):
    """Teilwert für die Bewertung des vorgeschlagenen Films: 0 bis RATING_WEIGHT."""
    return RATING_WEIGHT * candidate.rating / MAX_RATING


SCORE_PARTS = (genre_similarity, director_bonus, year_proximity, rating_bonus)


def similarity_score(base, candidate):
    """
    Summe aller Teilwerte.

    Args:
        base (Movie): Der Ausgangsfilm.
        candidate (Movie): Der verglichene Film.

    Returns:
        float: Der Ähnlichkeitswert von 0 bis 100, auf eine Stelle gerundet.
    """
    part_scores = map(lambda part: part(base, candidate), SCORE_PARTS)
    return round(reduce(add, part_scores, 0.0), 1)


def exclude_movie(movies, base):
    """Entfernt den Ausgangsfilm aus den Kandidaten."""
    return tuple(filter(lambda movie: movie_key(movie) != movie_key(base), movies))


def score_candidates(movies, base):
    """Berechnet für jeden Kandidaten den Ähnlichkeitswert zum Ausgangsfilm."""
    return tuple(map(lambda movie: Recommendation(movie, similarity_score(base, movie)), movies))


def keep_relevant(recommendations, min_score):
    """Behält nur Empfehlungen mit einem Wert von mindestens min_score."""
    return tuple(filter(lambda recommendation: recommendation.score >= min_score, recommendations))


def recommendation_rank(recommendation):
    """Sortierschlüssel: höchster Wert, dann beste Bewertung, dann Titel."""
    movie = recommendation.movie
    return (-recommendation.score, -movie.rating, movie.title.casefold())


def rank(recommendations):
    """Sortiert Empfehlungen mit recommendation_rank."""
    return tuple(sorted(recommendations, key=recommendation_rank))


def take(items, limit):
    """Liefert die ersten limit Elemente, bei negativem limit keine."""
    return items[:max(limit, 0)]


def recommend(movies, base, limit=DEFAULT_LIMIT, min_score=MIN_SCORE):
    """
    Empfiehlt ähnliche Filme.

    Args:
        movies (Sequence[Movie]): Der Katalog.
        base (Movie): Der Film, zu dem ähnliche Filme gesucht werden.
        limit (int): Die höchste Anzahl Empfehlungen.
        min_score (float): Der kleinste Ähnlichkeitswert einer Empfehlung.

    Returns:
        tuple[Recommendation, ...]: Die Empfehlungen, die ähnlichste zuerst.
    """
    return pipe(
        partial(exclude_movie, base=base),
        partial(score_candidates, base=base),
        partial(keep_relevant, min_score=min_score),
        rank,
        partial(take, limit=limit),
    )(movies)
