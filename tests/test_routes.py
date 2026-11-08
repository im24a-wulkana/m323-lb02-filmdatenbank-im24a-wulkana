"""Tests für die Routen."""

from app import create_app


def test_index_shows_title(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Filmdatenbank" in response.get_data(as_text=True)


def test_index_shows_import_summary_and_errors(tmp_path):
    path = tmp_path / "movies.csv"
    path.write_text(
        "title,year,genres,director,runtime,rating\n"
        "Heat,1995,Action,Michael Mann,170,8.3\n"
        "Alien,kein Jahr,Horror,Ridley Scott,117,8.5\n",
        encoding="utf-8",
    )

    page = create_app(path).test_client().get("/").get_data(as_text=True)

    assert "1 Filme importiert, 0 Duplikate entfernt, 1 Fehler" in page
    assert "Zeile 3" in page


def test_unknown_page_returns_404(client):
    response = client.get("/gibt-es-nicht")

    assert response.status_code == 404
