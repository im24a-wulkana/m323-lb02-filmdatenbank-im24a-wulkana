"""Routen der Filmdatenbank."""

from flask import Blueprint, abort, current_app, render_template, request

from app.catalog import SORT_OPTIONS, all_genres, average_rating, query_from_args, search_catalog
from app.recommender import recommend
from app.statistics import (GROUP_SORTS, decade_report, director_report, genre_report,
                            overview)

main = Blueprint("main", __name__)

STATS_SORT_OPTIONS = (
    ("count", "Anzahl Filme"),
    ("average", "Bewertung"),
    ("runtime", "Gesamtlaufzeit"),
    ("name", "Name"),
)


@main.route("/")
def index():
    """
    Zeigt die Startseite an.

    Returns:
        str: Die gerenderte Startseite.
    """
    return render_template("index.html", result=current_app.config["IMPORT_RESULT"])


@main.route("/movies")
def movies():
    """
    Zeigt den Katalog mit Suche, Filter und Sortierung an.

    Returns:
        str: Die gerenderte Katalogseite.
    """
    all_movies = current_app.config["IMPORT_RESULT"].movies
    found = search_catalog(all_movies, query_from_args(request.args))
    return render_template(
        "movies.html",
        movies=found,
        average=average_rating(found),
        genres=all_genres(all_movies),
        sort_options=SORT_OPTIONS,
    )


@main.route("/movies/<int:year>/<path:title>")
def movie_detail(year, title):
    """
    Zeigt einen Film mit ähnlichen Filmen an.

    Args:
        year (int): Das Erscheinungsjahr.
        title (str): Der Titel, die Grossschreibung zählt nicht.

    Returns:
        str: Die gerenderte Detailseite oder 404, wenn der Film fehlt.
    """
    movie = current_app.config["FIND_MOVIE"](title, year)
    if movie is None:
        abort(404)
    all_movies = current_app.config["IMPORT_RESULT"].movies
    return render_template("movie.html", movie=movie, recommendations=recommend(all_movies, movie))


@main.route("/stats")
def stats():
    """
    Zeigt Statistiken pro Genre, Jahrzehnt und Regie an.

    Returns:
        str: Die gerenderte Statistikseite.
    """
    all_movies = current_app.config["IMPORT_RESULT"].movies
    sort = request.args.get("sort", "count")
    return render_template(
        "stats.html",
        overview=overview(all_movies),
        genres=genre_report(all_movies, sort),
        decades=decade_report(all_movies),
        directors=director_report(all_movies),
        sort=sort if sort in GROUP_SORTS else "count",
        sort_options=STATS_SORT_OPTIONS,
    )
