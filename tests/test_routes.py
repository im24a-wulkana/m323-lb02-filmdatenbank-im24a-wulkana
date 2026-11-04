"""Tests für die Routen."""


def test_index_shows_title(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Filmdatenbank" in response.get_data(as_text=True)


def test_unknown_page_returns_404(client):
    response = client.get("/gibt-es-nicht")

    assert response.status_code == 404
