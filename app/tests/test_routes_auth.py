def test_register_and_login(client):
    register_payload = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "username": "testnewusername",
        "password": "testpassword123"
    }

    register_response = client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 200
    payload = register_response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"

    login_payload = {
        "username": "testuser",
        "password": "testpass123"
    }
    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

def test_register_duplicate_username(client):
    user_data = {
        "first_name": "dup_first_name",
        "last_name": "dup_last_name",
        "username": "dupuser",
        "password": "secret"
    }
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login_invalid_credentials(client):
    response = client.post("/auth/login", json={
        "username": "missingusername",
        "password": "wrongpass"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"
