from datetime import date, timedelta

import pytest

from app import create_app
from app.servicios import Restaurante


@pytest.fixture
def manana():
    return (date.today() + timedelta(days=1)).isoformat()


@pytest.fixture
def restaurante():
    return Restaurante()


@pytest.fixture
def cliente():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()
