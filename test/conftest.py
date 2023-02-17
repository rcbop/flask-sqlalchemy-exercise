import pytest
from api.app import create_app
from api.db import db

@pytest.fixture(scope="module")
def app_fixture():
    app = create_app("sqlite:///:memory:")
    app.config['TESTING'] = True
    with app.app_context():
        yield app

@pytest.fixture(scope="module")
def test_client(app_fixture):
    with app_fixture.test_client() as client:
        yield client

@pytest.fixture(scope="module")
def db_fixture(app_fixture):
    with app_fixture.app_context():
        db.create_all()
        yield db
        db.drop_all()