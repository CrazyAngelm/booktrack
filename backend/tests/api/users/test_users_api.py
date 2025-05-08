import uuid
import pytest
import requests

# Base URL for the locally running API
test_host = "http://localhost:8000/api"


@pytest.fixture(scope="module")
def unique_user():
    # Generate a unique user to avoid conflicts
    user = {
        "name": "John",
        "surname": "Doe",
        "email": f"{uuid.uuid4()}@example.com",
        "password": "securepassword"
    }
    yield user
    # Optionally implement teardown cleanup via delete endpoint if available


@pytest.fixture(scope="module")
def credentials(unique_user):
    return {"email": unique_user["email"], "password": unique_user["password"]}


# Register Endpoint Tests
def test_register_success(unique_user):
    # First-time registration should succeed and return tokens
    resp = requests.post(f"{test_host}/register", json=unique_user)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "access_token" in data
    assert "refresh_token_expires_in" in data


def test_register_duplicate(unique_user):
    # Registering the same user again should return conflict
    resp = requests.post(f"{test_host}/register", json=unique_user)
    assert resp.status_code == 409


# Login Endpoint Tests
def test_login_success(credentials):
    resp = requests.post(f"{test_host}/login", json=credentials)
    assert resp.status_code == 200
    token_resp = resp.json()
    assert isinstance(token_resp, dict)
    assert "access_token" in token_resp
    assert "refresh_token_expires_in" in token_resp


def test_login_validation_error():
    resp = requests.post(
        f"{test_host}/login", json={"email": "", "password": ""}
    )
    # Empty credentials should be unauthorized
    assert resp.status_code == 401
    assert "detail" in resp.json()


# Logout and Refresh Token Tests
def test_logout_invalid_token():
    # Invalid refresh_token should return 400
    resp = requests.post(
        f"{test_host}/logout", json={
            "refresh_token": "dummy_refresh_token"
        }
    )
    assert resp.status_code == 400


def test_logout_validation_error():
    # Missing refresh_token should trigger validation error
    resp = requests.post(f"{test_host}/logout", json={})
    assert resp.status_code == 422
    assert "detail" in resp.json()


# Refresh-Token Endpoint Tests
def test_refresh_token_invalid_token():
    # Invalid refresh_token should return 400
    resp = requests.post(
        f"{test_host}/refresh-token", json={
            "refresh_token": "dummy_refresh_token"
        }
    )
    assert resp.status_code == 400


def test_refresh_token_validation_error():
    # Missing refresh_token should trigger validation error
    resp = requests.post(f"{test_host}/refresh-token", json={})
    assert resp.status_code == 422
    assert "detail" in resp.json()
