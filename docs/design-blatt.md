# Design-Blatt: Empfehlungen „Ähnliche Filme“

Dieses Blatt ist vor der Umsetzung entstanden. Es beschreibt, *was* das Feature liefern soll, und nicht, *wie* Schleifen oder Variablen aussehen.

## Problem

Auf der Detailseite eines Films sollen bis zu fünf ähnliche Filme aus dem Katalog vorgeschlagen werden. Die Vorschläge müssen nachvollziehbar sein, deshalb wird zu jedem Vorschlag ein Ähnlichkeitswert von 0 bis 100 angezeigt.

## Deklarative Anforderungen

1. Die Empfehlungen für einen Film F sind **alle Filme des Katalogs ausser F**, deren Ähnlichkeitswert zu F **mindestens 40** beträgt.
2. Der Ähnlichkeitswert ist die **Summe von vier Teilwerten**:
   - Genre-Übereinstimmung: Anteil gemeinsamer Genres an allen Genres beider Filme (Jaccard), mal 50
   - Gleiche Regie: 20, sonst 0
   - Zeitliche Nähe: 15, linear abnehmend bis 0 bei 30 Jahren Abstand
   - Qualität des Vorschlags: Bewertung des vorgeschlagenen Films / 10, mal 15
3. Die Empfehlungen sind **nach Ähnlichkeit absteigend** geordnet, bei Gleichstand nach Bewertung absteigend, dann nach Titel.
4. Es werden **höchstens N** Empfehlungen geliefert (Standard 5).
5. Der Katalog und der Ausgangsfilm werden **nicht verändert**. Gleiche Eingabe ergibt immer dieselbe Ausgabe.
6. Ein leerer Katalog, ein Katalog nur mit F oder N = 0 ergeben **keine Empfehlungen** und keinen Fehler.

## Unveränderliche Datentypen

| Typ | Felder | Bemerkung |
|---|---|---|
| `Movie` | title, year, genres, director, runtime, rating | existiert bereits, `frozen=True` |
| `Recommendation` | movie: Movie, score: float | neu, `frozen=True`, verbindet Film und Wert |

Konstruktor: `Recommendation(movie, score)` wird nur in `score_candidates` erzeugt.

## Datenfluss

```
Katalog (tuple[Movie])
   │  exclude_movie       F selbst entfernen
   ▼
Kandidaten (tuple[Movie])
   │  score_candidates    jeden Kandidaten mit F vergleichen
   ▼
Bewertete Kandidaten (tuple[Recommendation])
   │  keep_relevant       Wert >= 40
   ▼
Relevante Kandidaten
   │  rank                nach Wert, Bewertung, Titel sortieren
   ▼
Rangliste
   │  take                die ersten N
   ▼
Empfehlungen (tuple[Recommendation])
```

## Geplante Operatoren

Alle Operatoren sind pure functions. Jeder nimmt das Ergebnis des vorherigen als erstes Argument, so lassen sie sich mit `pipe` aus `app/functional.py` zu einem Ablauf zusammensetzen.

| Operator | Signatur | Aufgabe |
|---|---|---|
| `genre_similarity` | `(Movie, Movie) -> float` | Teilwert Genres, 0 bis 50 |
| `director_bonus` | `(Movie, Movie) -> float` | Teilwert Regie, 0 oder 20 |
| `year_proximity` | `(Movie, Movie) -> float` | Teilwert Jahr, 0 bis 15 |
| `rating_bonus` | `(Movie, Movie) -> float` | Teilwert Bewertung, 0 bis 15 |
| `similarity_score` | `(Movie, Movie) -> float` | Summe aller Teilwerte, gerundet auf eine Stelle |
| `exclude_movie` | `(tuple[Movie], Movie) -> tuple[Movie]` | Ausgangsfilm entfernen (`filter`) |
| `score_candidates` | `(tuple[Movie], Movie) -> tuple[Recommendation]` | Werte berechnen (`map`) |
| `keep_relevant` | `(tuple[Recommendation], float) -> tuple[Recommendation]` | Schwelle anwenden (`filter`) |
| `rank` | `(tuple[Recommendation]) -> tuple[Recommendation]` | sortieren (`sorted` mit `key`) |
| `take` | `(tuple, int) -> tuple` | die ersten N |
| `recommend` | `(tuple[Movie], Movie, int, float) -> tuple[Recommendation]` | Komposition aller Schritte |

Die vier Teilwerte haben dieselbe Signatur. Deshalb können sie in einem Tupel `SCORE_PARTS` gespeichert und gemeinsam aufsummiert werden. Ein neuer Teilwert braucht dann nur eine neue Funktion im Tupel.

## Geplante Testfälle

| Eingabe | Erwartete Ausgabe |
|---|---|
| F = „Alien“, Kandidat mit gleichen Genres, gleicher Regie, gleichem Jahr | Wert = 50 + 20 + 15 + Bewertung·1.5 |
| Kandidat ohne gemeinsames Genre, 40 Jahre Abstand, andere Regie | Wert unter 40, wird weggelassen |
| Katalog enthält nur F | `()` |
| leerer Katalog | `()` |
| N = 0 | `()` |
| zwei Kandidaten mit gleichem Wert | der besser bewertete zuerst |
