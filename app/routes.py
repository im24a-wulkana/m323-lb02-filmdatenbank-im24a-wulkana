"""Routen der Filmdatenbank."""

from flask import Blueprint, current_app, render_template, request

from app.catalog import SORT_OPTIONS, all_genres, average_rating, query_from_args, search_catalog

main = Blueprint("main", __name__)


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
