"""Filmdatenbank: Flask-Applikation für das Praxisprojekt der LB02 in Modul 323."""

from flask import Flask

from app.routes import main


def create_app():
    """
    Erstellt und konfiguriert die Flask-Applikation.

    Returns:
        Flask: Die fertig konfigurierte Applikation.
    """
    app = Flask(__name__)
    app.register_blueprint(main)
    return app
