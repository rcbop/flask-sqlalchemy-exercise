import pytest
from api.app import create_app
from flask_jwt_extended import create_access_token
from api.db import db

TEST_JWT_KEY = "test_jwt_key"


@pytest.fixture(scope="module")
def app_fixture():
    app = create_app("sqlite:///:memory:", TEST_JWT_KEY)
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


@pytest.fixture(scope="module")
def auth_header() -> dict:
    access_token = create_access_token(identity=1, fresh=True)
    headers = {'Authorization': 'Bearer ' + access_token}
    return headers