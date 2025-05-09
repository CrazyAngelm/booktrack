# backend/locustfile.py
from locust import HttpUser, task, between
import requests


def register_user(name: str, surname: str, email: str, password: str):
    body = {
        "name": name,
        "surname": surname,
        "email": email,
        "password": password
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.post(
        "http://localhost:8000/api/register",
        json=body,
        headers=headers
    )
    if response.status_code == 200:
        print(f"User with email {email} registered successfully.")
    else:
        raise Exception(f"Failed to register user with email {email}: {response.status_code} - {response.text}")

    return response.json().get("access_token")


def login_user(email: str, password: str):
    body = {
        "email": email,
        "password": password
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.post(
        "http://localhost:8000/api/login",
        json=body,
        headers=headers
    )
    if response.status_code == 200:
        print(f"User with email {email} logged in successfully.")
    else:
        print(f"Failed to login user with email {email}: {response.status_code} - {response.text}")

    return response.json().get("access_token")

try:
    access_token = register_user("John", "Doe", "john@gmail.com", "123456")
except:
    access_token = login_user("john@gmail.com", "123456")

class BookTrackUser(HttpUser):
    # emulate a realistic think time between requests
    wait_time = between(3, 10)
    

    @task(3)
    def list_books(self):
        # hit the paginated discovery endpoint
        self.client.get("/api/books/", name="GET /api/books", headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    @task(1)
    def get_book(self):
        # fetch a specific book
        self.client.get("/api/books/book-id/1", name="GET /api/books/book-id/:id", headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
