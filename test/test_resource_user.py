from api.models import UserModel
import pytest

@pytest.fixture
def user_fixture(db_fixture):
    user = UserModel(username="test", password="test")
    db_fixture.session.add(user)
    db_fixture.session.commit()
    yield user
    db_fixture.session.query(UserModel).delete()

def test_register_user(test_client, db_fixture):
    user_data = {"username": "test", "password": "test"}
    response = test_client.post("/register", json=user_data)
    assert response.status_code == 201
    assert response.json["message"] == "User registered!"
    assert db_fixture.session.query(UserModel).count() == 1
    db_fixture.session.query(UserModel).delete()

def test_get_user(test_client, user_fixture, auth_header):
    response = test_client.get("/user/1", headers=auth_header)
    assert response.status_code == 200
    assert response.json["username"] == "test"

def test_delete_user(test_client, db_fixture, user_fixture, auth_header):
    response = test_client.delete("/user/1", headers=auth_header)
    assert response.status_code == 202
    assert response.json["message"] == "User deleted!"
    assert db_fixture.session.query(UserModel).count() == 0