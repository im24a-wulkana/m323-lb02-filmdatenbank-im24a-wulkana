"""Gemeinsame Fixtures für die Tests."""

import pytest

from app import create_app


@pytest.fixture(name="client")
def fixture_client():
    """Liefert einen Test-Client der Applikation."""
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()
