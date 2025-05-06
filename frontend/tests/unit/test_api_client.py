import pytest
import requests
import os
import sys
import importlib
import app.api_client as api_client
from app.config import settings
# Ensure project root is on PYTHONPATH so that `app` package is discoverable
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '../..'
            )
        )
    )

dummy_books = [
    {'id': 1, 'title': 'Book1'},
    {'id': 2, 'title': 'Book2'},
    {'id': 3, 'title': 'Book3'},
]
dummy_details = {1: {'id': 1, 'title': 'Book1', 'desc': 'A'},
                 2: {'id': 2, 'title': 'Book2', 'desc': 'B'}}
dummy_fav = [dummy_details[1]]
dummy_rl = [{'id': 2, 'title': 'Book2', 'desc': 'B', 'status': 'reading'}]


class DummyResp:
    def __init__(self, ok, json_data):
        self.ok = ok
        self._json = json_data

    def raise_for_status(self):
        if not self.ok:
            raise requests.HTTPError()

    def json(self):
        return self._json


@pytest.fixture(autouse=True)
def reload_api_client(monkeypatch):
    # Enable fake data and inject dummy data
    monkeypatch.setattr(settings, 'USE_FAKE_DATA', True)
    monkeypatch.setattr(settings, 'PER_PAGE', 2)
    # Reload module so FAKE_* are imported
    importlib.reload(api_client)
    # Override fake data
    api_client.FAKE_BOOKS[:] = list(dummy_books)
    api_client.FAKE_DETAILS.clear()
    api_client.FAKE_DETAILS.update(dummy_details)
    api_client.FAKE_FAV[:] = list(dummy_fav)
    api_client.FAKE_RL[:] = list(dummy_rl)
    return api_client


def test_api_get_list_pages(reload_api_client):
    api_client = reload_api_client
    # Page 1
    res1 = api_client.api_get('/books/', params={'page': 1})
    assert res1['results'] == dummy_books[0:2]
    assert res1['total_pages'] == 2
    # Page 2
    res2 = api_client.api_get('/books/', params={'page': 2})
    assert res2['results'] == dummy_books[2:4]


def test_api_get_details(reload_api_client):
    api_client = reload_api_client
    details = api_client.api_get('/books/2')
    assert details == dummy_details[2]


def test_api_get_favourites_and_rl(reload_api_client):
    api_client = reload_api_client
    fav = api_client.api_get('/favourites/')
    assert fav == dummy_fav
    rl = api_client.api_get('/reading-list/')
    assert rl == dummy_rl


def test_api_post_fake_favourites(reload_api_client):
    api_client = reload_api_client
    # Add book 2 to favourites
    ok = api_client.api_post('/favourites/', json={'book_id': 2})
    assert ok is True
    assert dummy_details[2] in api_client.FAKE_FAV


def test_api_put_fake_reading_list_update_and_add(reload_api_client):
    api_client = reload_api_client
    # Update existing
    ok1 = api_client.api_put('/reading-list/2', json={'status': 'completed'})
    assert ok1 is True
    assert any(
        item['id'] == 2
        and item['status'] == 'completed'
        for item in api_client.FAKE_RL
    )
    # Add new
    ok2 = api_client.api_put('/reading-list/1', json={'status': 'planned'})
    assert ok2 is True
    assert any(
        item['id'] == 1 and item['status'] == 'planned'
        for item in api_client.FAKE_RL
    )


def test_api_delete_fake_favourites_and_rl(reload_api_client):
    api_client = reload_api_client
    # Delete fav id 1
    ok1 = api_client.api_delete('/favourites/1')
    assert ok1 is True
    assert all(f['id'] != 1 for f in api_client.FAKE_FAV)
    # Delete rl id 2
    ok2 = api_client.api_delete('/reading-list/2')
    assert ok2 is True
    assert all(r['id'] != 2 for r in api_client.FAKE_RL)

# Tests for real API fallback


def setup_fallback(monkeypatch):
    monkeypatch.setattr(settings, 'USE_FAKE_DATA', False)
    importlib.reload(api_client)
    return api_client


@pytest.mark.parametrize('ok, data, exp', [
    (True, {'x': 1}, {'x': 1}),
    (False, None, pytest.raises(requests.HTTPError))
])
def test_api_get_fallback(monkeypatch, ok, data, exp):
    api_client = setup_fallback(monkeypatch)
    calls = {}

    def fake_get(url, params):
        calls['url'] = url
        calls['params'] = params
        return DummyResp(ok, data)
    monkeypatch.setattr(requests, 'get', fake_get)
    if ok:
        res = api_client.api_get('/test', {'a': 1})
        assert res == data
    else:
        with exp:
            api_client.api_get('/test')
    assert '/test' in calls['url']


@pytest.mark.parametrize('ok', [True, False])
def test_api_post_fallback(monkeypatch, ok):
    api_client = setup_fallback(monkeypatch)
    calls = {}

    def fake_post(url, json):
        calls['url'] = url
        calls['json'] = json
        return DummyResp(ok, None)
    monkeypatch.setattr(requests, 'post', fake_post)
    res = api_client.api_post('/p', json={'a': 2})
    assert res == ok
    assert '/p' in calls['url']


@pytest.mark.parametrize('ok', [True, False])
def test_api_put_fallback(monkeypatch, ok):
    api_client = setup_fallback(monkeypatch)
    calls = {}

    def fake_put(url, json):
        calls['url'] = url
        calls['json'] = json
        return DummyResp(ok, None)
    monkeypatch.setattr(requests, 'put', fake_put)
    res = api_client.api_put('/u', json={'b': 3})
    assert res == ok
    assert '/u' in calls['url']


@pytest.mark.parametrize('ok', [True, False])
def test_api_delete_fallback(monkeypatch, ok):
    api_client = setup_fallback(monkeypatch)
    calls = {}

    def fake_delete(url):
        calls['url'] = url
        return DummyResp(ok, None)
    monkeypatch.setattr(requests, 'delete', fake_delete)
    res = api_client.api_delete('/d/5')
    assert res == ok
    assert '/d/5' in calls['url']
