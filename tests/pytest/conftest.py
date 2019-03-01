import pytest
import flaskr
from unittest import mock


@pytest.fixture
def app():
    app = flaskr.create_app()
    return app

@pytest.fixture
def client(app):
    return app.test_client()
