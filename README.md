# Filmdatenbank

Flask-Applikation für das Praxisprojekt der LB02 im Modul 323 (Funktional Programmieren).

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Starten

```bash
flask --app app run --debug
```

Die Applikation läuft danach unter http://127.0.0.1:5000.

## Daten

`data/movies.csv` enthält reale Filme. Titel, Jahr, Genres, Regie und Laufzeit sind von Hand erfasst, die Bewertungen sind Richtwerte auf einer Skala von 0 bis 10 und keine offiziellen Werte einer Filmplattform.

## Tests

```bash
pytest
pylint app
```
