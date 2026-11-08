# Messungen

Gemessen mit `python scripts/benchmark.py` auf demselben Rechner (Python 3.14.2, Windows 11, AMD64). Die Testdaten sind synthetisch und reproduzierbar (fester Zufallsstartwert), rund zehn Prozent davon sind Duplikate. Angegeben ist der Bestwert aus drei Durchläufen.

## Vorher: Listen-Scan

Stand: Commit „CSV-Export und Messung der Listen-Scans“.

- `remove_duplicates` in `app/importer.py`: `reduce` mit `keep_first`. Für jeden Film prüft `any(...)` alle bisher eindeutigen Filme, und `(*unique, movie)` kopiert das ganze Tupel. Aufwand O(n²).
- `make_lookup` in `app/catalog.py`: `next(...)` durchsucht bei jeder Suche die Filme von vorne. Aufwand O(n) pro Suche.

| Filme | Duplikate entfernen | 1000 Suchen |
|---:|---:|---:|
| 1'000 | 33.8 ms | 53.4 ms |
| 2'000 | 122.0 ms | 90.5 ms |
| 4'000 | 616.8 ms | 259.5 ms |

Doppelt so viele Filme brauchen beim Entfernen der Duplikate etwa vier- bis fünfmal so lange. Das passt zum quadratischen Aufwand. Die Suche wächst ungefähr linear mit der Anzahl Filme.
