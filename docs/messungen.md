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

## Nachher: Hash-basierte Datenstrukturen

Stand: Commit „Duplikaterkennung und Filmsuche mit Dictionary optimieren“.

- `remove_duplicates`: ein lokales Dictionary `first_by_key` mit `setdefault`. Pro Film eine Hash-Abfrage, Aufwand O(n). Weil Dictionaries die Einfügereihenfolge behalten, bleibt die Reihenfolge der ersten Vorkommen erhalten.
- `make_lookup`: baut einmal ein Dictionary `index` von `(titel, jahr)` auf den Film. Jede Suche ist danach eine Hash-Abfrage, Aufwand O(1). Durch `reversed(...)` gewinnt bei gleichen Schlüsseln das erste Vorkommen, wie vorher bei `next(...)`.
- Die Tests in `tests/` sind seit dem Vorher-Commit unverändert und laufen weiterhin durch (82 bestanden).

| Filme | Duplikate entfernen | 1000 Suchen |
|---:|---:|---:|
| 1'000 | 0.2 ms | 0.3 ms |
| 2'000 | 0.5 ms | 0.3 ms |
| 4'000 | 0.7 ms | 0.2 ms |

Zusatzmessung mit demselben Skript:

| Filme | Duplikate entfernen | Index aufbauen (einmalig) |
|---:|---:|---:|
| 4'000 | 0.7 ms | 0.7 ms |
| 100'000 | 76.3 ms | 67.1 ms |

## Vergleich

| 4'000 Filme | Vorher | Nachher | Faktor |
|---|---:|---:|---:|
| Duplikate entfernen | 616.8 ms | 0.7 ms | rund 880 |
| 1000 Suchen | 259.5 ms | 0.2 ms | rund 1300 |

Der Aufbau des Index kostet einmalig etwa so viel wie das Entfernen der Duplikate. In der App passiert das nur beim Start in `create_app`. Danach ist jede Suche praktisch gratis. Der Preis ist zusätzlicher Speicher für ein zweites Verzeichnis aller Filme.
