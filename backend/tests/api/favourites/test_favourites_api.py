import uuid
import pytest
import requests

API_BASE = "http://localhost:8000/api"
BOOKS_PATH = f"{API_BASE}/books"
FAV_PATH = f"{API_BASE}/favourites"


@pytest.fixture(scope="module")
def test_user():
    user = {
        "name": "Fav",
        "surname": "Tester",
        "email": f"fav_{uuid.uuid4()}@example.com",
        "password": "favpassword"
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
def favourite_record(auth_header, book_id):
    r = requests.post(f"{FAV_PATH}?book_id={book_id}", headers=auth_header)
    assert r.status_code == 201, "Unexpected response: " + str(r.status_code) + ", " + r.text
    return r.json()


def test_get_favourites_empty_then_after(auth_header, book_id,
                                         favourite_record):
    r1 = requests.get(FAV_PATH, headers=auth_header)
    assert r1.status_code == 200
    data1 = r1.json()
    assert isinstance(data1, dict)

    r2 = requests.get(FAV_PATH, headers=auth_header)
    assert r2.status_code == 200
    data2 = r2.json()
    assert isinstance(data2, dict)
    book_ids = [fav["book_id"] for fav in data2.get("favourites", [])]
    assert book_id in book_ids


def test_post_favourite_validation_error(auth_header):
    r = requests.post(FAV_PATH, headers=auth_header)
    assert r.status_code == 422
    assert "detail" in r.json()


def test_get_favourite_by_book_id_success(auth_header,
                                          book_id, favourite_record):
    r = requests.get(f"{FAV_PATH}/book-id/{book_id}", headers=auth_header)
    assert r.status_code == 200
    fav = r.json()
    assert fav.get("book_id") == book_id
    assert fav.get("user_email")
    assert isinstance(fav.get("created_at"), str)
    assert isinstance(fav.get("id"), int)


def test_get_favourite_by_book_id_not_found(auth_header):
    r = requests.get(f"{FAV_PATH}/book-id/999999", headers=auth_header)
    assert r.status_code == 404


def test_get_favourite_by_book_id_validation_error(auth_header):
    r = requests.get(f"{FAV_PATH}/book-id/abc", headers=auth_header)
    assert r.status_code == 422
    assert "detail" in r.json()


def test_put_favourite_success(auth_header, book_id, favourite_record):
    r = requests.put(
        f"{FAV_PATH}/book-id/{book_id}?is_favourite={False}",
        headers=auth_header)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)


def test_put_favourite_validation_error_missing(auth_header, book_id):
    r = requests.put(f"{FAV_PATH}/book-id/{book_id}",
                     headers=auth_header, json={})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_put_favourite_validation_error_invalid_flag(auth_header, book_id):
    payload = {"is_favourite": "yes"}
    r = requests.put(f"{FAV_PATH}/book-id/{book_id}",
                     headers=auth_header, json=payload)
    assert r.status_code == 422
    assert "detail" in r.json()
