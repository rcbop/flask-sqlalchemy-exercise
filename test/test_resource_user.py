from api.models import UserModel
from passlib.hash import pbkdf2_sha256
import pytest

@pytest.fixture
def user_fixture(db_fixture):
    user = UserModel(
        username="test",
        password=pbkdf2_sha256.hash("test"))
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

def test_register_user_invalid_request(test_client, db_fixture):
    user_data = {"username": "test"}
    response = test_client.post("/register", json=user_data)
    assert response.status_code == 422

def test_register_user_already_exists(test_client, user_fixture):
    user_data = {"username": "test", "password": "test"}
    response = test_client.post("/register", json=user_data)
    assert response.status_code == 409
    assert response.json["message"] == "Username already exists"

def test_get_user(test_client, user_fixture, auth_header):
    response = test_client.get("/user/1", headers=auth_header)
    assert response.status_code == 200
    assert response.json["username"] == "test"

def test_get_user_not_found(test_client, auth_header):
    response = test_client.get("/user/1", headers=auth_header)
    assert response.status_code == 404
    assert response.json["message"] == "User not found"

def test_delete_user(test_client, db_fixture, user_fixture, auth_header):
    response = test_client.delete("/user/1", headers=auth_header)
    assert response.status_code == 202
    assert response.json["message"] == "User deleted!"
    assert db_fixture.session.query(UserModel).count() == 0

def test_delete_user_not_found(test_client, auth_header):
    response = test_client.delete("/user/99", headers=auth_header)
    assert response.status_code == 404
    assert response.json["message"] == "User not found"


def test_login_user(test_client, user_fixture):
    user_data = {"username": "test", "password": "test"}
    response = test_client.post("/login", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json
    assert "refresh_token" in response.json

def test_login_user_invalid_password(test_client, user_fixture):
    user_data = {"username": "test", "password": "wrong"}
    response = test_client.post("/login", json=user_data)
    assert response.status_code == 401

def test_login_invalid_user(test_client, user_fixture):
    user_data = {"username": "wrong", "password": "test"}
    response = test_client.post("/login", json=user_data)
    assert response.status_code == 401

@pytest.fixture
def tokens(test_client, user_fixture):
    user_data = {"username": "test", "password": "test"}
    response = test_client.post("/login", json=user_data)
    assert response.status_code == 200
    access_token = response.json["access_token"]
    refresh_token = response.json["refresh_token"]
    return (access_token, refresh_token)

def test_logout_user(test_client, tokens):
    response = test_client.post("/logout", headers={"Authorization": f"Bearer {tokens[0]}"})
    assert response.status_code == 200
    response = test_client.get("/user/1", headers={"Authorization": f"Bearer {tokens[0]}"})
    assert response.status_code == 401

def test_refresh_token(test_client, tokens):
    response = test_client.post("/refresh", headers={"Authorization": f"Bearer {tokens[1]}"})
    assert response.status_code == 200
    assert "access_token" in response.json