"""Tests für das Datenmodell."""

from dataclasses import FrozenInstanceError

import pytest

from app.models import Movie, movie_from_row, parse_genres, parse_rating, parse_year

VALID_ROW = {
    "title": " Heat ",
    "year": "1995",
    "genres": "Action| Krimi |",
    "director": "Michael Mann",
    "runtime": "170",
    "rating": "8.3",
}


def test_movie_from_row_converts_all_fields():
    assert movie_from_row(VALID_ROW) == Movie(
        title="Heat",
        year=1995,
        genres=("Action", "Krimi"),
        director="Michael Mann",
        runtime=170,
        rating=8.3,
    )


def test_movie_is_immutable():
    movie = movie_from_row(VALID_ROW)

    with pytest.raises(FrozenInstanceError):
        movie.rating = 1.0


@pytest.mark.parametrize("field, value", [
    ("title", "   "),
    ("year", "kein Jahr"),
    ("year", "1500"),
    ("genres", "|"),
    ("director", ""),
    ("runtime", "0"),
    ("rating", "10.1"),
])
def test_movie_from_row_rejects_invalid_field(field, value):
    with pytest.raises(ValueError):
        movie_from_row({**VALID_ROW, field: value})


def test_movie_from_row_rejects_missing_column():
    row = {key: value for key, value in VALID_ROW.items() if key != "year"}

    with pytest.raises(ValueError):
        movie_from_row(row)


def test_movie_from_row_rejects_too_many_columns():
    with pytest.raises(ValueError, match="zu viele Spalten"):
        movie_from_row({**VALID_ROW, None: ["zusätzlich"]})


def test_parse_limits_are_inclusive():
    assert parse_year("1888") == 1888
    assert parse_rating("0") == 0.0
    assert parse_rating("10") == 10.0


def test_parse_genres_without_value_fails():
    with pytest.raises(ValueError):
        parse_genres(None)
