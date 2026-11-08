"""Allgemeine Hilfsfunktionen für funktionale Komposition."""

from functools import reduce


def identity(value):
    """Gibt den Wert unverändert zurück."""
    return value


def pipe(*functions):
    """
    Verkettet Funktionen von links nach rechts zu einer neuen Funktion.

    pipe(f, g, h)(x) entspricht h(g(f(x))).

    Args:
        *functions (Callable): Die Funktionen in Ausführungsreihenfolge.

    Returns:
        Callable: Die zusammengesetzte Funktion.
    """
    return reduce(compose_two, functions, identity)


def compose_two(first, second):
    """
    Setzt zwei Funktionen zusammen: zuerst first, dann second.

    Args:
        first (Callable): Die zuerst ausgeführte Funktion.
        second (Callable): Die danach ausgeführte Funktion.

    Returns:
        Callable: Eine Funktion, die second(first(value)) berechnet.
    """
    return lambda value: second(first(value))
