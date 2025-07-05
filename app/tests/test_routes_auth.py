import pytest
from fastapi.testclient import TestClient


def test_register_and_login(client: TestClient):  # Happy path testing for register and login
    register_payload = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "username": "testnewuser",
        "password": "testpassword123",
    }
    register_response = client.post("/auth/register", json=register_payload)  # Register user
    assert register_response.status_code == 200
    register_data = register_response.json()
    assert "access_token" in register_data
    assert register_data["token_type"] == "bearer"

    login_payload = {
        "username": register_payload["username"],
        "password": register_payload["password"],
    }
    login_response = client.post("/auth/login", json=login_payload)  # Login user
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"


def test_register_duplicate_username(client: TestClient):  # Testing if duplicates can be made
    user_data = {
        "first_name": "dup_first_name",
        "last_name": "dup_last_name",
        "username": "dupuser",
        "password": "secret123",
    }
    resp1 = client.post("/auth/register", json=user_data)
    assert resp1.status_code == 200

    resp2 = client.post("/auth/register", json=user_data)  # registering the same information again
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Username already registered"


def test_login_invalid_credentials(client: TestClient):  # Checking if login function with incorrect credentials
    resp1 = client.post(
        "/auth/login", json={"username": "nonexistent", "password": "nonexistentpass"}
    )
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Invalid credentials"

    valid_user = {"first_name": "first", "last_name": "last", "username": "correctuser", "password": "correctpass123"}
    client.post("/auth/register", json=valid_user)
    resp2 = client.post(
        "/auth/login", json={"username": "correctuser", "password": "wrongpass"}
    )
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Invalid credentials"

def test_register_without_last_name(client: TestClient):  # Testing if you can register without inputing a last name
    payload = {"first_name": "first_no_last", "username": "no_last", "password": "no_last"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 200
    assert resp.json()["access_token"]

def test_register_short_password(client: TestClient):  # Minimum 6 characters for password enforcement
    payload = {"first_name": "first", "username": "usershortpass", "password": "12345"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 422
