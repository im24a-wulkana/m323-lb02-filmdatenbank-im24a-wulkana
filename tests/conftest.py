"""Gemeinsame Fixtures für die Tests."""

import pytest

from app import create_app

CATALOG_CSV = (
    "title,year,genres,director,runtime,rating\n"
    "Heat,1995,Action|Krimi,Michael Mann,170,8.3\n"
    "Alien,1979,Horror|Science-Fiction,Ridley Scott,117,8.5\n"
    "Aliens,1986,Action|Science-Fiction,James Cameron,137,8.4\n"
    "Fargo,1996,Krimi|Thriller,Joel Coen,98,8.1\n"
    "Up,2009,Animation|Komödie,Pete Docter,96,8.3\n"
)


@pytest.fixture(name="client")
def fixture_client():
    """Liefert einen Test-Client der Applikation."""
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


@pytest.fixture(name="catalog_client")
def fixture_catalog_client(tmp_path):
    """Liefert einen Test-Client mit fünf bekannten Filmen."""
    path = tmp_path / "movies.csv"
    path.write_text(CATALOG_CSV, encoding="utf-8")
    app = create_app(path)
    app.config.update(TESTING=True)
    return app.test_client()
