"""Tests für den CSV-Export."""

from app import DEFAULT_DATA_PATH
from app.exporter import export_movies, movie_to_row
from app.importer import import_movies, load_movies
from app.models import Movie

HEAT = Movie("Heat", 1995, ("Action", "Krimi"), "Michael Mann", 170, 8.3)


def test_movie_to_row_formats_every_field():
    assert movie_to_row(HEAT) == {
        "title": "Heat",
        "year": "1995",
        "genres": "Action|Krimi",
        "director": "Michael Mann",
        "runtime": "170",
        "rating": "8.3",
    }


def test_export_writes_header_and_quotes_commas():
    movie = Movie("The Good, the Bad and the Ugly", 1966, ("Western",), "Sergio Leone", 178, 8.8)

    assert export_movies((movie,)) == (
        "title,year,genres,director,runtime,rating\n"
        '"The Good, the Bad and the Ugly",1966,Western,Sergio Leone,178,8.8\n'
    )


def test_export_of_no_movies_is_only_header():
    assert export_movies(()) == "title,year,genres,director,runtime,rating\n"


def test_export_and_import_round_trip_with_project_data():
    movies = load_movies(DEFAULT_DATA_PATH).movies

    assert import_movies(export_movies(movies)).movies == movies


def test_export_route_uses_catalog_filters(catalog_client):
    response = catalog_client.get("/export?genre=Krimi&sort=title&order=asc")

    assert response.mimetype == "text/csv"
    assert "attachment" in response.headers["Content-Disposition"]
    assert response.get_data(as_text=True).splitlines()[1:] == [
        "Fargo,1996,Krimi|Thriller,Joel Coen,98,8.1",
        "Heat,1995,Action|Krimi,Michael Mann,170,8.3",
    ]
