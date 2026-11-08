"""Tests für den CSV-Import."""

from app import DEFAULT_DATA_PATH
from app.importer import RowError, import_movies, load_movies

HEADER = "title,year,genres,director,runtime,rating\n"
HEAT = "Heat,1995,Action|Krimi,Michael Mann,170,8.3\n"
ALIEN = "Alien,1979,Horror,Ridley Scott,117,8.5\n"


def test_import_reads_valid_movies_in_order():
    result = import_movies(HEADER + HEAT + ALIEN)

    assert [movie.title for movie in result.movies] == ["Heat", "Alien"]
    assert result.errors == ()
    assert result.duplicates == 0


def test_import_keeps_valid_rows_and_reports_invalid_row():
    result = import_movies(HEADER + HEAT + "Alien,kein Jahr,Horror,Ridley Scott,117,8.5\n")

    assert [movie.title for movie in result.movies] == ["Heat"]
    assert len(result.errors) == 1
    assert result.errors[0].line == 3


def test_import_reports_real_line_number_after_blank_line():
    result = import_movies(HEADER + HEAT + "\n" + "Alien,1979,,Ridley Scott,117,8.5\n")

    assert result.errors == (RowError(4, "Mindestens ein Genre ist nötig"),)


def test_import_removes_duplicates_ignoring_case():
    result = import_movies(HEADER + HEAT + ALIEN + "HEAT,1995,Drama,Michael Mann,170,5.0\n")

    assert [movie.title for movie in result.movies] == ["Heat", "Alien"]
    assert result.movies[0].rating == 8.3
    assert result.duplicates == 1


def test_import_keeps_same_title_from_other_year():
    result = import_movies(HEADER + HEAT + "Heat,1986,Action,Dick Richards,101,5.0\n")

    assert len(result.movies) == 2
    assert result.duplicates == 0


def test_import_handles_quoted_comma_in_title():
    row = '"The Good, the Bad and the Ugly",1966,Western,Sergio Leone,178,8.8\n'

    assert import_movies(HEADER + row).movies[0].title == "The Good, the Bad and the Ugly"


def test_import_of_empty_text_returns_empty_result():
    result = import_movies("")

    assert result.movies == ()
    assert result.errors == ()
    assert result.duplicates == 0


def test_load_movies_ignores_byte_order_mark(tmp_path):
    path = tmp_path / "movies.csv"
    path.write_text(HEADER + HEAT, encoding="utf-8-sig")

    assert load_movies(path).movies[0].title == "Heat"


def test_project_data_imports_without_problems():
    result = load_movies(DEFAULT_DATA_PATH)

    assert len(result.movies) >= 100
    assert result.errors == ()
    assert result.duplicates == 0
