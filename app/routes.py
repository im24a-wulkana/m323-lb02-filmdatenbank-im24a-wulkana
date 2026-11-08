"""Routen der Filmdatenbank."""

from flask import (Blueprint, Response, abort, current_app, redirect, render_template, request,
                   url_for)

from app.catalog import (SORT_OPTIONS, all_genres, average_rating, make_lookup, query_from_args,
                         replace_movie, search_catalog)
from app.exporter import export_movies
from app.importer import import_summary
from app.models import parse_rating, with_rating
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


def store_movies(config, catalog):
    """
    Legt den aktuellen Katalog und seine Suchfunktion in der Konfiguration ab.

    Das ist die einzige Stelle, an der sich der Zustand der App ändert.

    Args:
        config (flask.Config): Die Konfiguration der App.
        catalog (tuple[Movie, ...]): Der neue Katalog.
    """
    config["MOVIES"] = catalog
    config["FIND_MOVIE"] = make_lookup(catalog)


def current_movies():
    """Liefert den aktuellen Katalog."""
    return current_app.config["MOVIES"]


def find_movie_or_404(title, year):
    """Liefert den Film zu Titel und Jahr oder bricht mit 404 ab."""
    movie = current_app.config["FIND_MOVIE"](title, year)
    if movie is None:
        abort(404)
    return movie


@main.route("/")
def index():
    """
    Zeigt die Startseite an.

    Returns:
        str: Die gerenderte Startseite.
    """
    result = current_app.config["IMPORT_RESULT"]
    return render_template("index.html", result=result, summary=import_summary(result))


@main.route("/movies")
def movies():
    """
    Zeigt den Katalog mit Suche, Filter und Sortierung an.

    Returns:
        str: Die gerenderte Katalogseite.
    """
    all_movies = current_movies()
    found = search_catalog(all_movies, query_from_args(request.args))
    return render_template(
        "movies.html",
        movies=found,
        average=average_rating(found),
        genres=all_genres(all_movies),
        sort_options=SORT_OPTIONS,
    )


@main.route("/export")
def export():
    """
    Exportiert die Filme des Katalogs mit denselben Filtern wie die Katalogseite.

    Returns:
        Response: Die CSV-Datei als Download.
    """
    found = search_catalog(current_movies(), query_from_args(request.args))
    return Response(
        export_movies(found),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=filme.csv"},
    )


def render_detail(movie, error=None):
    """Rendert die Detailseite eines Films mit Empfehlungen."""
    return render_template(
        "movie.html",
        movie=movie,
        recommendations=recommend(current_movies(), movie),
        error=error,
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
    return render_detail(find_movie_or_404(title, year))


@main.post("/rating")
def update_rating():
    """
    Ändert die Bewertung eines Films, ohne den alten Film zu verändern.

    Returns:
        Response: Eine Weiterleitung zur Detailseite, bei ungültiger Bewertung
        die Detailseite mit Fehlermeldung und Status 400.
    """
    movie = find_movie_or_404(request.form.get("title", ""), request.form.get("year", type=int))
    try:
        rating = parse_rating(request.form.get("rating"))
    except ValueError:
        return render_detail(movie, "Die Bewertung muss eine Zahl zwischen 0 und 10 sein."), 400
    updated = with_rating(movie, rating)
    store_movies(current_app.config, replace_movie(current_movies(), updated))
    return redirect(url_for("main.movie_detail", year=updated.year, title=updated.title))


@main.route("/stats")
def stats():
    """
    Zeigt Statistiken pro Genre, Jahrzehnt und Regie an.

    Returns:
        str: Die gerenderte Statistikseite.
    """
    all_movies = current_movies()
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
