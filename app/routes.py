"""Routen der Filmdatenbank."""

from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """
    Zeigt die Startseite an.

    Returns:
        str: Die gerenderte Startseite.
    """
    return render_template("index.html")
