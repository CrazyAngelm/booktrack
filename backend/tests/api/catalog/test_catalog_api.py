import uuid
import pytest
import requests

# Base URL of the local API
API_BASE = "http://localhost:8000/api"
BOOKS_PATH = f"{API_BASE}/books"

# -- Fixtures for auth


@pytest.fixture(scope="module")
def test_user():
    # Register a fresh user for catalog tests
    user = {
        "name": "Test",
        "surname": "User",
        "email": f"books_{uuid.uuid4()}@example.com",
        "password": "testpassword"
    }
    # Register
    r = requests.post(f"{API_BASE}/register", json=user)
    assert r.status_code == 200
    return user


@pytest.fixture(scope="module")
def auth_token(test_user):
    # Login to get access token
    creds = {"email": test_user["email"], "password": test_user["password"]}
    r = requests.post(f"{API_BASE}/login", json=creds)
    assert r.status_code == 200
    data = r.json()
    token = data.get("access_token")
    assert token, "Login did not return access_token"
    return token


@pytest.fixture
def auth_header(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# Helper to validate a book object
def validate_book(item):
    assert isinstance(item, dict)
    expected_keys = {"title", "subjects", "authors", "summaries",
                     "translators", "languages", "copyright", "media_type",
                     "formats", "download_count", "id"}
    assert expected_keys.issubset(item.keys())
    # Basic type checks
    assert isinstance(item["title"], str)
    assert isinstance(item["subjects"], list)
    assert isinstance(item["authors"], list)
    assert isinstance(item["summaries"], list)
    assert isinstance(item["translators"], list)
    assert isinstance(item["languages"], list)
    assert isinstance(item["copyright"], bool)
    assert isinstance(item["media_type"], str)
    assert isinstance(item["formats"], dict)
    assert isinstance(item["download_count"], int)
    assert isinstance(item["id"], int)


# 1. GET /api/books
def test_get_books_default(auth_header):
    resp = requests.get(BOOKS_PATH, headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if data:
        validate_book(data[0])


def test_get_books_pagination_params(auth_header):
    params = {"page_no": 2, "page_size": 5}
    resp = requests.get(BOOKS_PATH, headers=auth_header, params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Expect a list; pagination behavior may vary by dataset size


def test_get_books_invalid_params(auth_header):
    resp = requests.get(
        BOOKS_PATH, headers=auth_header, params={"page_no": "abc"}
    )
    assert resp.status_code == 422
    assert "detail" in resp.json()


# 2. GET /api/books/book-id/{book_id}
def test_get_book_by_id_success(auth_header):
    # Create a known book or assume id=1 exists
    resp = requests.get(f"{BOOKS_PATH}/book-id/1", headers=auth_header)
    assert resp.status_code == 200
    book = resp.json()
    validate_book(book)


def test_get_book_by_id_not_found(auth_header):
    resp = requests.get(f"{BOOKS_PATH}/book-id/999999", headers=auth_header)
    assert resp.status_code in (404,)


def test_get_book_by_id_validation_error(auth_header):
    resp = requests.get(f"{BOOKS_PATH}/book-id/abc", headers=auth_header)
    assert resp.status_code == 422
    assert "detail" in resp.json()


# 3. GET /api/books/search
def test_search_success(auth_header):
    params = {"query": "history"}
    resp = requests.get(
        f"{BOOKS_PATH}/search", headers=auth_header, params=params
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if data:
        validate_book(data[0])


def test_search_pagination_and_query(auth_header):
    params = {"query": "science", "page_no": 1, "page_size": 2}
    resp = requests.get(
        f"{BOOKS_PATH}/search", headers=auth_header, params=params
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Expect a list; pagination behavior may vary by dataset size


def test_search_validation_error_missing_query(auth_header):
    resp = requests.get(f"{BOOKS_PATH}/search", headers=auth_header)
    assert resp.status_code == 422
    assert "detail" in resp.json()


def test_search_validation_error_invalid_page(auth_header):
    params = {"query": "math", "page_size": "NaN"}
    resp = requests.get(
        f"{BOOKS_PATH}/search", headers=auth_header, params=params
    )
    assert resp.status_code == 422
    assert "detail" in resp.json()
