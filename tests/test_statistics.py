"""Tests für die Statistiken."""

import re

from app.functional import pipe
from app.models import Movie
from app.statistics import (GroupStats, Overview, decade_report, director_report, genre_report,
                            group_by, movie_genres, overview)

HEAT = Movie("Heat", 1995, ("Action", "Krimi"), "Michael Mann", 170, 8.3)
ALIEN = Movie("Alien", 1979, ("Horror", "Science-Fiction"), "Ridley Scott", 117, 8.5)
ALIENS = Movie("Aliens", 1986, ("Action", "Science-Fiction"), "James Cameron", 137, 8.4)
FARGO = Movie("Fargo", 1996, ("Krimi", "Thriller"), "Joel Coen", 98, 8.1)
BLADE_RUNNER = Movie("Blade Runner", 1982, ("Science-Fiction",), "Ridley Scott", 117, 8.1)
MOVIES = (HEAT, ALIEN, ALIENS, FARGO, BLADE_RUNNER)


def test_pipe_runs_functions_left_to_right():
    assert pipe(lambda x: x + 1, lambda x: x * 10)(2) == 30
    assert pipe()(5) == 5


def test_group_by_puts_movie_in_every_genre():
    groups = group_by(MOVIES, movie_genres)

    assert groups["Action"] == (HEAT, ALIENS)
    assert groups["Science-Fiction"] == (ALIEN, ALIENS, BLADE_RUNNER)


def test_group_by_without_movies_is_empty():
    assert group_by((), movie_genres) == {}


def test_genre_report_by_count_breaks_ties_by_rating():
    names = [stats.name for stats in genre_report(MOVIES, "count")]

    assert names == ["Science-Fiction", "Action", "Krimi", "Horror", "Thriller"]


def test_genre_report_values():
    science_fiction = genre_report(MOVIES, "count")[0]

    assert science_fiction == GroupStats("Science-Fiction", 3, 8.33, 371, "Alien")


def test_genre_report_by_average_and_unknown_sort():
    by_average = [stats.name for stats in genre_report(MOVIES, "average")]

    assert by_average == ["Horror", "Action", "Science-Fiction", "Krimi", "Thriller"]
    assert genre_report(MOVIES, "budget") == genre_report(MOVIES, "count")


def test_genre_report_by_runtime():
    assert genre_report(MOVIES, "runtime")[0].name == "Science-Fiction"


def test_decade_report_is_chronological():
    assert [stats.name for stats in decade_report(MOVIES)] == ["1970er", "1980er", "1990er"]


def test_director_report_keeps_only_directors_with_two_movies():
    assert director_report(MOVIES) == (GroupStats("Ridley Scott", 2, 8.3, 234, "Alien"),)


def test_overview():
    assert overview(MOVIES) == Overview(5, 8.3, 639)
    assert overview(()) == Overview(0, None, 0)


def test_stats_page_sorts_genres(catalog_client):
    page = catalog_client.get("/stats?sort=name").get_data(as_text=True)
    genre_section = page.split("<h2>Genres</h2>")[1].split("<h2>")[0]

    assert re.findall(r'class="group">([^<]+)', genre_section) == [
        "Action", "Animation", "Horror", "Komödie", "Krimi", "Science-Fiction", "Thriller",
    ]
    assert "5 Filme · Durchschnitt 8.3" in page
