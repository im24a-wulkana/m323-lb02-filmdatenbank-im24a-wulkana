"""Tests für die Katalogfunktionen."""

from app.catalog import (CatalogQuery, active_filters, all_genres, average_rating, make_lookup,
                         parse_optional_float, query_from_args, search_catalog)
from app.models import Movie

HEAT = Movie("Heat", 1995, ("Action", "Krimi"), "Michael Mann", 170, 8.3)
ALIEN = Movie("Alien", 1979, ("Horror",), "Ridley Scott", 117, 8.5)
FARGO = Movie("Fargo", 1996, ("Krimi",), "Joel Coen", 98, 8.1)
MOVIES = (HEAT, ALIEN, FARGO)


def test_query_from_args_cleans_values():
    args = {"q": "  HeAt ", "genre": "Krimi", "min_rating": "8", "sort": "year", "order": "asc"}

    assert query_from_args(args) == CatalogQuery("heat", "Krimi", 8.0, "year", False)


def test_query_from_args_uses_defaults_for_invalid_values():
    assert query_from_args({"sort": "budget", "min_rating": "inf"}) == CatalogQuery()


def test_parse_optional_float():
    assert parse_optional_float("7.5") == 7.5
    assert parse_optional_float(None) is None
    assert parse_optional_float("nan") is None


def test_active_filters_only_for_set_criteria():
    assert active_filters(CatalogQuery()) == ()
    assert len(active_filters(CatalogQuery(text="heat", min_rating=0.0))) == 2


def test_search_catalog_combines_filters():
    query = CatalogQuery(genre="Krimi", min_rating=8.2)

    assert search_catalog(MOVIES, query) == (HEAT,)


def test_search_catalog_returns_new_tuple_and_keeps_input():
    result = search_catalog(MOVIES, CatalogQuery(sort="title", descending=False))

    assert result == (ALIEN, FARGO, HEAT)
    assert MOVIES == (HEAT, ALIEN, FARGO)


def test_average_rating():
    assert average_rating(MOVIES) == 8.3
    assert average_rating(()) is None


def test_all_genres_unique_and_sorted():
    assert all_genres(MOVIES) == ("Action", "Horror", "Krimi")


def test_lookup_finds_movie_ignoring_case():
    lookup = make_lookup(MOVIES)

    assert lookup("fargo", 1996) == FARGO
    assert lookup("Fargo", 1997) is None
    assert make_lookup(())("Fargo", 1996) is None


def test_lookup_returns_first_of_equal_keys():
    remake = Movie("FARGO", 1996, ("Drama",), "Andere Regie", 90, 5.0)

    assert make_lookup((FARGO, remake))("Fargo", 1996) == FARGO
