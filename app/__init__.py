"""Filmdatenbank: Flask-Applikation für das Praxisprojekt der LB02 in Modul 323."""

from pathlib import Path

from flask import Flask

from app.importer import load_movies
from app.routes import main

DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "movies.csv"


def create_app(data_path=DEFAULT_DATA_PATH):
    """
    Erstellt und konfiguriert die Flask-Applikation.

    Args:
        data_path (str | Path): Der Pfad zur CSV-Datei mit den Filmen.

    Returns:
        Flask: Die fertig konfigurierte Applikation.
    """
    app = Flask(__name__)
    app.config["IMPORT_RESULT"] = load_movies(data_path)
    app.register_blueprint(main)
    return app
