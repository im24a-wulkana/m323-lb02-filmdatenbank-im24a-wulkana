"""Verhaltenstests für die Katalogseite.

Die Tests prüfen nur, was die Seite anzeigt, und nicht, wie die Route intern
arbeitet. So bleiben sie beim Refactoring der Route unverändert gültig.
"""

import re

TITLE_PATTERN = re.compile(r'class="title">(?:<a [^>]*>)?([^<]+)')


def titles(client, query=""):
    """Liefert die Filmtitel der Katalogseite in angezeigter Reihenfolge."""
    page = client.get(f"/movies{query}").get_data(as_text=True)
    return TITLE_PATTERN.findall(page)


def test_default_sorts_by_rating_descending_and_keeps_ties_in_order(catalog_client):
    assert titles(catalog_client) == ["Alien", "Aliens", "Heat", "Up", "Fargo"]


def test_search_ignores_case_and_matches_title(catalog_client):
    assert titles(catalog_client, "?q=ALIEN") == ["Alien", "Aliens"]


def test_search_matches_director(catalog_client):
    assert titles(catalog_client, "?q=coen") == ["Fargo"]


def test_genre_filter(catalog_client):
    assert titles(catalog_client, "?genre=Krimi") == ["Heat", "Fargo"]


def test_min_rating_filter_includes_limit(catalog_client):
    assert titles(catalog_client, "?min_rating=8.4") == ["Alien", "Aliens"]


def test_invalid_min_rating_is_ignored(catalog_client):
    assert len(titles(catalog_client, "?min_rating=abc")) == 5
    assert len(titles(catalog_client, "?min_rating=nan")) == 5


def test_sort_by_title_ascending(catalog_client):
    assert titles(catalog_client, "?sort=title&order=asc") == ["Alien", "Aliens", "Fargo", "Heat", "Up"]


def test_sort_by_year_descending(catalog_client):
    assert titles(catalog_client, "?sort=year") == ["Up", "Fargo", "Heat", "Aliens", "Alien"]


def test_sort_by_runtime_ascending(catalog_client):
    assert titles(catalog_client, "?sort=runtime&order=asc") == ["Up", "Fargo", "Alien", "Aliens", "Heat"]


def test_unknown_sort_falls_back_to_rating(catalog_client):
    assert titles(catalog_client, "?sort=budget") == titles(catalog_client)


def test_combined_filters_and_sort(catalog_client):
    query = "?genre=Action&min_rating=8&sort=year&order=asc"

    assert titles(catalog_client, query) == ["Aliens", "Heat"]


def test_summary_shows_count_and_average(catalog_client):
    page = catalog_client.get("/movies").get_data(as_text=True)

    assert "5 Filme · Durchschnitt 8.3" in page


def test_no_results_shows_message(catalog_client):
    page = catalog_client.get("/movies?q=matrix").get_data(as_text=True)

    assert "Keine Filme gefunden." in page
    assert "Durchschnitt" not in page


def test_genre_select_lists_each_genre_once_sorted(catalog_client):
    page = catalog_client.get("/movies").get_data(as_text=True)
    options = re.findall(r'<option value="([^"]+)"', page.split('name="genre"')[1].split("</select>")[0])

    assert options == ["Action", "Animation", "Horror", "Komödie", "Krimi", "Science-Fiction", "Thriller"]
