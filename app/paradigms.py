"""Dieselbe Aufgabe in drei Paradigmen: Durchschnittsbewertung pro Genre.

Die App verwendet die funktionale Variante aus app/statistics.py. Die OO- und
die prozedurale Variante stehen hier zum Vergleich und werden in
tests/test_paradigms.py auf dasselbe Ergebnis geprüft.
"""

from app.statistics import genre_report


class GenreAverageCalculator:
    """Objektorientiert: ein Objekt sammelt Zustand und bietet Methoden dafür an."""

    def __init__(self):
        self._sums = {}
        self._counts = {}

    def add(self, movie):
        """Nimmt einen Film in die Berechnung auf und verändert dabei den Zustand."""
        for genre in movie.genres:
            self._sums[genre] = self._sums.get(genre, 0.0) + movie.rating
            self._counts[genre] = self._counts.get(genre, 0) + 1

    def averages(self):
        """Liefert die Durchschnitte der bisher aufgenommenen Filme."""
        return {genre: round(self._sums[genre] / self._counts[genre], 2) for genre in sorted(self._sums)}


def genre_averages_oo(movies):
    """Durchschnitt pro Genre mit GenreAverageCalculator."""
    calculator = GenreAverageCalculator()
    for movie in movies:
        calculator.add(movie)
    return calculator.averages()


def genre_averages_procedural(movies):
    """Prozedural: Schritt für Schritt mit Schleifen und veränderbaren Variablen."""
    sums = {}
    counts = {}
    for movie in movies:
        for genre in movie.genres:
            if genre not in sums:
                sums[genre] = 0.0
                counts[genre] = 0
            sums[genre] += movie.rating
            counts[genre] += 1
    result = {}
    for genre in sorted(sums):
        result[genre] = round(sums[genre] / counts[genre], 2)
    return result


def genre_averages_functional(movies):
    """Funktional: Komposition aus group_by, summarize_groups und sorted in genre_report."""
    return {stats.name: stats.average_rating for stats in genre_report(movies, sort="name")}


def set_rating_in_place(movies, title, year, rating):
    """
    Mutierende Variante zum Vergleich mit models.with_rating.

    Die Filme sind hier veränderbare Dictionaries. Die Funktion gibt nichts
    zurück, sondern ändert das gefundene Dictionary direkt.

    Args:
        movies (list[dict]): Die Filme als Dictionaries.
        title (str): Der Titel des Films.
        year (int): Das Jahr des Films.
        rating (float): Die neue Bewertung.
    """
    for movie in movies:
        if movie["title"] == title and movie["year"] == year:
            movie["rating"] = rating
