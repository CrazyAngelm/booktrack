import uuid
import pytest
import requests

API_BASE = "http://localhost:8000/api"
BOOKS_PATH = f"{API_BASE}/books"
READING_PATH = f"{API_BASE}/reading-list"


@pytest.fixture(scope="module")
def test_user():
    user = {
        "name": "Read",
        "surname": "Tester",
        "email": f"read_{uuid.uuid4()}@example.com",
        "password": "readpassword"
    }
    r = requests.post(f"{API_BASE}/register", json=user)
    assert r.status_code == 200
    return user


@pytest.fixture(scope="module")
def auth_token(test_user):
    creds = {"email": test_user["email"], "password": test_user["password"]}
    r = requests.post(f"{API_BASE}/login", json=creds)
    assert r.status_code == 200
    token = r.json().get("access_token")
    assert token
    return token


@pytest.fixture(scope="module")
def auth_header(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="module")
def book_id(auth_header):
    r = requests.get(BOOKS_PATH, headers=auth_header)
    assert r.status_code == 200
    books = r.json()
    assert isinstance(books, list) and books, "No books available for testing"
    return books[0]["id"]


@pytest.fixture(scope="module")
def reading_record(auth_header, book_id):
    payload = {"book_id": book_id, "status": "Want"}
    r = requests.post(READING_PATH, headers=auth_header, params=payload)

    # If creation fails, delete and retry
    if r.status_code in {400, 422}:
        del_resp = requests.delete(
            f"{READING_PATH}/book-id/{book_id}", headers=auth_header)
        assert del_resp.status_code in {
            200, 404}, f"Failed to clean previous state: {del_resp.text}"
        r = requests.post(READING_PATH, headers=auth_header, params=payload)

    assert r.status_code == 201, f"Failed to create reading record: {
        r.status_code} {r.text}"
    return r.json()


def test_get_reading_list_initial_and_after_add(auth_header):
    r1 = requests.get(READING_PATH, headers=auth_header)
    assert r1.status_code == 200
    data1 = r1.json()
    assert isinstance(data1, dict)

    r2 = requests.get(READING_PATH, headers=auth_header)
    assert r2.status_code == 200
    data2 = r2.json()
    assert isinstance(data2, dict)
    assert "favourites" not in data2


def test_post_reading_validation_error(auth_header):
    r = requests.post(READING_PATH, headers=auth_header)
    assert r.status_code == 422
    assert "detail" in r.json()


def test_get_reading_by_book_id_success(auth_header, book_id, reading_record):
    r = requests.get(f"{READING_PATH}/book-id/{book_id}", headers=auth_header)
    assert r.status_code == 200
    rec = r.json()
    assert rec.get("book_id") == book_id
    assert rec.get("status")


def test_get_reading_by_book_id_not_found(auth_header):
    r = requests.get(f"{READING_PATH}/book-id/999999", headers=auth_header)
    assert r.status_code == 404


def test_get_reading_by_book_id_validation_error(auth_header):
    r = requests.get(f"{READING_PATH}/book-id/abc", headers=auth_header)
    assert r.status_code == 422
    assert "detail" in r.json()


def test_put_reading_status_success(auth_header, book_id, reading_record):
    params = {"status": "Reading"}
    r = requests.put(f"{READING_PATH}/book-id/{book_id}",
                     headers=auth_header, params=params)
    assert r.status_code == 200
    rec = r.json()
    assert rec.get("status") == "Reading"


def test_put_reading_status_validation_error(auth_header, book_id):
    r = requests.put(f"{READING_PATH}/book-id/{book_id}", headers=auth_header)
    assert r.status_code == 422
    assert "detail" in r.json()


def test_delete_reading_success(auth_header, book_id, reading_record):
    r = requests.delete(
        f"{READING_PATH}/book-id/{book_id}", headers=auth_header)
    assert r.status_code == 200
    rec = r.json()
    assert rec.get("book_id") == book_id


def test_delete_reading_validation_error(auth_header):
    r = requests.delete(f"{READING_PATH}/book-id/abc", headers=auth_header)
    assert r.status_code == 422
    assert "detail" in r.json()


def test_get_reading_by_status_success(auth_header):
    r = requests.get(f"{READING_PATH}/status/Reading", headers=auth_header)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)


def test_get_reading_by_status_validation_error(auth_header):
    r = requests.get(f"{READING_PATH}/status/", headers=auth_header)
    assert r.status_code == 404
