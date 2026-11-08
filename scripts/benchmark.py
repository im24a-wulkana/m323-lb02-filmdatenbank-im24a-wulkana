"""Misst Duplikaterkennung und Filmsuche mit synthetischen Daten.

Aufruf aus dem Projektordner:
    python scripts/benchmark.py
"""

import platform
import random
import sys
import timeit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# pylint: disable=wrong-import-position
from app.catalog import make_lookup
from app.importer import remove_duplicates
from app.models import Movie

SIZES = (1_000, 2_000, 4_000)
LOOKUPS = 1_000
REPEAT = 3
GENRES = ("Action", "Drama", "Komödie", "Krimi", "Science-Fiction", "Thriller")


def synthetic_movies(count, seed=323):
    """
    Erzeugt reproduzierbare Testfilme, davon rund zehn Prozent Duplikate.

    Args:
        count (int): Die Anzahl Filme inklusive Duplikate.
        seed (int): Der Startwert des Zufallsgenerators.

    Returns:
        tuple[Movie, ...]: Die gemischten Filme.
    """
    rng = random.Random(seed)
    originals = tuple(
        Movie(
            title=f"Film {number}",
            year=rng.randint(1920, 2025),
            genres=(rng.choice(GENRES),),
            director=f"Regie {number % 300}",
            runtime=rng.randint(70, 200),
            rating=round(rng.uniform(1, 10), 1),
        )
        for number in range(count * 9 // 10)
    )
    duplicates = tuple(rng.choice(originals) for _ in range(count - len(originals)))
    movies = list(originals + duplicates)
    rng.shuffle(movies)
    return tuple(movies)


def best_time(function):
    """Liefert die beste von REPEAT Laufzeiten in Millisekunden."""
    return min(timeit.repeat(function, number=1, repeat=REPEAT)) * 1000


def measure(size):
    """
    Misst beide Operationen für eine Datenmenge.

    Args:
        size (int): Die Anzahl Filme.

    Returns:
        tuple[float, float]: Millisekunden für Duplikate entfernen und für LOOKUPS Suchen.
    """
    movies = synthetic_movies(size)
    unique = remove_duplicates(movies)
    rng = random.Random(size)
    targets = tuple(rng.choice(unique) for _ in range(LOOKUPS))
    lookup = make_lookup(unique)
    dedupe_ms = best_time(lambda: remove_duplicates(movies))
    lookup_ms = best_time(lambda: [lookup(movie.title, movie.year) for movie in targets])
    return dedupe_ms, lookup_ms


def main():
    """Gibt die Messwerte als Markdown-Tabelle aus."""
    print(f"Python {platform.python_version()} auf {platform.system()} {platform.release()}, "
          f"{platform.processor() or platform.machine()}")
    print(f"Bestwert aus {REPEAT} Durchläufen\n")
    print(f"| Filme | Duplikate entfernen | {LOOKUPS} Suchen |")
    print("|---:|---:|---:|")
    for size in SIZES:
        dedupe_ms, lookup_ms = measure(size)
        print(f"| {size:,} | {dedupe_ms:,.1f} ms | {lookup_ms:,.1f} ms |".replace(",", "'"))


if __name__ == "__main__":
    main()
