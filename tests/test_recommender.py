"""Tests für die Empfehlungen."""

import pytest

from app.models import Movie
from app.recommender import (Recommendation, director_bonus, genre_similarity, rank,
                             rating_bonus, recommend, similarity_score, take, year_proximity)

ALIEN = Movie("Alien", 1979, ("Horror", "Science-Fiction"), "Ridley Scott", 117, 8.5)
BLADE_RUNNER = Movie("Blade Runner", 1982, ("Action", "Drama", "Science-Fiction"), "Ridley Scott", 117, 8.1)
THE_SHINING = Movie("The Shining", 1980, ("Horror", "Drama"), "Stanley Kubrick", 146, 8.4)
UP = Movie("Up", 2009, ("Animation", "Komödie"), "Pete Docter", 96, 8.3)
CATALOG = (ALIEN, BLADE_RUNNER, THE_SHINING, UP)


def test_genre_similarity_is_jaccard_index():
    assert genre_similarity(ALIEN, BLADE_RUNNER) == pytest.approx(12.5)
    assert genre_similarity(ALIEN, ALIEN) == 50
    assert genre_similarity(ALIEN, UP) == 0


def test_director_bonus():
    assert director_bonus(ALIEN, BLADE_RUNNER) == 20
    assert director_bonus(ALIEN, UP) == 0


def test_year_proximity_decreases_to_zero():
    assert year_proximity(ALIEN, BLADE_RUNNER) == pytest.approx(13.5)
    assert year_proximity(ALIEN, UP) == 0


def test_rating_bonus_uses_candidate_rating():
    assert rating_bonus(ALIEN, BLADE_RUNNER) == pytest.approx(12.15)


def test_similarity_score_is_sum_of_parts():
    assert similarity_score(ALIEN, BLADE_RUNNER) == 58.1
    perfect_match = Movie("Alien Director's Cut", 1979, ALIEN.genres, "Ridley Scott", 117, 10.0)
    assert similarity_score(ALIEN, perfect_match) == 100


def test_recommend_excludes_base_filters_and_ranks():
    result = recommend(CATALOG, ALIEN)

    assert result == (Recommendation(BLADE_RUNNER, 58.1), Recommendation(THE_SHINING, 43.8))


def test_recommend_respects_limit():
    assert recommend(CATALOG, ALIEN, limit=1) == (Recommendation(BLADE_RUNNER, 58.1),)


@pytest.mark.parametrize("movies, limit", [
    ((), 5),
    ((ALIEN,), 5),
    (CATALOG, 0),
    (CATALOG, -3),
])
def test_recommend_edge_cases_return_nothing(movies, limit):
    assert recommend(movies, ALIEN, limit=limit) == ()


def test_recommend_without_similar_movies():
    assert recommend(CATALOG, UP) == ()


def test_rank_breaks_ties_by_rating_then_title():
    tied = (
        Recommendation(UP, 50.0),
        Recommendation(THE_SHINING, 50.0),
        Recommendation(BLADE_RUNNER, 60.0),
    )

    assert [entry.movie.title for entry in rank(tied)] == ["Blade Runner", "The Shining", "Up"]


def test_take():
    assert take((1, 2, 3), 2) == (1, 2)
    assert take((1, 2, 3), 10) == (1, 2, 3)


def test_detail_page_shows_movie_and_recommendations(catalog_client):
    page = catalog_client.get("/movies/1979/alien").get_data(as_text=True)

    assert "<h1>Alien" in page
    assert 'class="recommendation"' in page


def test_detail_page_of_unknown_movie_returns_404(catalog_client):
    assert catalog_client.get("/movies/1979/Matrix").status_code == 404
