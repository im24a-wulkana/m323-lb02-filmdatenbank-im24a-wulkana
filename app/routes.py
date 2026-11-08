"""Routen der Filmdatenbank."""

import math

from flask import Blueprint, current_app, render_template, request

main = Blueprint("main", __name__)

SORT_OPTIONS = (
    ("rating", "Bewertung"),
    ("year", "Jahr"),
    ("title", "Titel"),
    ("runtime", "Laufzeit"),
)


@main.route("/")
def index():
    """
    Zeigt die Startseite an.

    Returns:
        str: Die gerenderte Startseite.
    """
    return render_template("index.html", result=current_app.config["IMPORT_RESULT"])


def sort_value(movie, sort):
    """Liefert den Wert, nach dem ein Film sortiert wird."""
    if sort == "title":
        return movie.title.casefold()
    if sort == "year":
        return movie.year
    if sort == "runtime":
        return movie.runtime
    return movie.rating


def comes_before(first, second, sort, descending):
    """Prüft, ob first in der Sortierung vor second steht."""
    if descending:
        return sort_value(first, sort) > sort_value(second, sort)
    return sort_value(first, sort) < sort_value(second, sort)


@main.route("/movies")
def movies():
    """
    Zeigt den Katalog mit Suche, Filter und Sortierung an.

    Returns:
        str: Die gerenderte Katalogseite.
    """
    all_movies = current_app.config["IMPORT_RESULT"].movies

    text = request.args.get("q", "").strip().casefold()
    genre = request.args.get("genre", "")
    try:
        min_rating = float(request.args.get("min_rating", ""))
        if not math.isfinite(min_rating):
            min_rating = None
    except ValueError:
        min_rating = None
    sort = request.args.get("sort", "rating")
    if sort not in ("rating", "year", "title", "runtime"):
        sort = "rating"
    descending = request.args.get("order", "desc") != "asc"

    found = []
    for movie in all_movies:
        if text and text not in movie.title.casefold() and text not in movie.director.casefold():
            continue
        if genre and genre not in movie.genres:
            continue
        if min_rating is not None and movie.rating < min_rating:
            continue
        found.append(movie)

    for i in range(1, len(found)):
        current = found[i]
        j = i - 1
        while j >= 0 and comes_before(current, found[j], sort, descending):
            found[j + 1] = found[j]
            j -= 1
        found[j + 1] = current

    average = None
    if found:
        total = 0.0
        for movie in found:
            total += movie.rating
        average = round(total / len(found), 1)

    genres = []
    for movie in all_movies:
        for movie_genre in movie.genres:
            if movie_genre not in genres:
                genres.append(movie_genre)
    genres.sort()

    return render_template(
        "movies.html",
        movies=found,
        average=average,
        genres=genres,
        sort_options=SORT_OPTIONS,
    )
