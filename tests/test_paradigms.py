"""Tests für den Paradigmenvergleich und die Bewertungsänderung."""

from dataclasses import FrozenInstanceError

import pytest

from app import DEFAULT_DATA_PATH
from app.catalog import replace_movie
from app.importer import load_movies
from app.models import Movie, with_rating
from app.paradigms import (genre_averages_functional, genre_averages_oo,
                           genre_averages_procedural, set_rating_in_place)

HEAT = Movie("Heat", 1995, ("Action", "Krimi"), "Michael Mann", 170, 8.3)
FARGO = Movie("Fargo", 1996, ("Krimi",), "Joel Coen", 98, 8.1)


def test_all_paradigms_give_the_same_result_on_project_data():
    movies = load_movies(DEFAULT_DATA_PATH).movies

    oo_result = genre_averages_oo(movies)

    assert oo_result == genre_averages_procedural(movies) == genre_averages_functional(movies)
    assert list(oo_result) == sorted(oo_result)


def test_paradigms_on_small_example():
    expected = {"Action": 8.3, "Krimi": 8.2}

    assert genre_averages_oo((HEAT, FARGO)) == expected
    assert genre_averages_procedural((HEAT, FARGO)) == expected
    assert genre_averages_functional((HEAT, FARGO)) == expected


def test_all_paradigms_handle_empty_catalog():
    assert genre_averages_oo(()) == genre_averages_procedural(()) == genre_averages_functional(()) == {}


def test_mutation_changes_every_reference():
    heat = {"title": "Heat", "year": 1995, "rating": 8.3}
    catalog = [heat]
    favourites = [heat]

    set_rating_in_place(catalog, "Heat", 1995, 5.0)

    assert favourites[0]["rating"] == 5.0


def test_with_rating_keeps_original_unchanged():
    updated = with_rating(HEAT, 5.0)

    assert updated == Movie("Heat", 1995, ("Action", "Krimi"), "Michael Mann", 170, 5.0)
    assert HEAT.rating == 8.3
    with pytest.raises(FrozenInstanceError):
        HEAT.rating = 5.0


def test_replace_movie_returns_new_catalog():
    catalog = (HEAT, FARGO)

    new_catalog = replace_movie(catalog, with_rating(FARGO, 9.0))

    assert new_catalog == (HEAT, with_rating(FARGO, 9.0))
    assert new_catalog[0] is HEAT
    assert catalog == (HEAT, FARGO)


def test_rating_route_updates_catalog(catalog_client):
    response = catalog_client.post("/rating", data={"title": "Heat", "year": "1995", "rating": "9.5"})

    assert response.status_code == 302
    detail = catalog_client.get(response.headers["Location"]).get_data(as_text=True)
    assert '<dd class="rating">9.5</dd>' in detail
    assert "Durchschnitt 8.6" in catalog_client.get("/movies").get_data(as_text=True)


def test_rating_route_rejects_invalid_rating(catalog_client):
    response = catalog_client.post("/rating", data={"title": "Heat", "year": "1995", "rating": "11"})

    assert response.status_code == 400
    assert '<dd class="rating">8.3</dd>' in response.get_data(as_text=True)


def test_rating_route_for_unknown_movie_returns_404(catalog_client):
    response = catalog_client.post("/rating", data={"title": "Matrix", "year": "1999", "rating": "8"})

    assert response.status_code == 404
