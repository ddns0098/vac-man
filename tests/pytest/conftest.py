import pytest
from flaskr import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.from_object('instance.config')
    return app
