import streamlit as st
import pytest
import requests

from frontend import app

# Fixtures to isolate session state


def setup_function():
    # Reset session state before each test
    for key in list(st.session_state.keys()):
        del st.session_state[key]


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, text=''):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        return self._json

# clear_auth


def test_clear_auth():
    st.session_state['access_token'] = 'a'
    st.session_state['refresh_token'] = 'r'
    st.session_state['token_expiry'] = 123
    st.session_state['user_email'] = 'e'
    app.clear_auth()
    assert st.session_state['access_token'] is None
    assert st.session_state['refresh_token'] is None
    assert st.session_state['token_expiry'] is None
    assert st.session_state['user_email'] is None

# get_headers


def test_get_headers_no_token():
    st.session_state.pop('access_token', None)
    headers = app.get_headers()
    assert headers == {'Content-Type': 'application/json'}


def test_get_headers_with_token():
    st.session_state['access_token'] = 'tok'
    headers = app.get_headers()
    assert headers == {'Content-Type': 'application/json',
                       'Authorization': 'Bearer tok'}

# refresh_access_token


def test_refresh_access_token_no_rt():
    st.session_state.pop('refresh_token', None)
    assert app.refresh_access_token() is False


def test_refresh_access_token_success(monkeypatch):
    st.session_state['refresh_token'] = 'rt'

    def post(url, json, timeout):
        return DummyResponse(200, {'access_token': 'new', 'expires_in': 3600})
    monkeypatch.setattr(app.session, 'post', post)
    result = app.refresh_access_token()
    assert result is True
    assert st.session_state['access_token'] == 'new'
    assert st.session_state['token_expiry'] == 3600


def test_refresh_access_token_failure(monkeypatch):
    st.session_state['refresh_token'] = 'rt'

    def post(url, json, timeout):
        return DummyResponse(400, {'detail': 'bad'})
    monkeypatch.setattr(app.session, 'post', post)
    st.session_state['access_token'] = 'old'
    assert app.refresh_access_token() is False
    assert st.session_state['access_token'] is None

# api_request


def test_api_request_network_error(monkeypatch):
    monkeypatch.setattr(app.session, 'request', lambda *args, **
                        kwargs: (_ for _ in ()).throw(
                            requests.RequestException("fail")))
    called = {}
    monkeypatch.setattr(st, 'error', lambda msg: called.setdefault('msg', msg))
    assert app.api_request('GET', '/path') is None
    assert 'Network error' in called['msg']


def test_api_request_401_and_refresh(monkeypatch):
    calls = {'count': 0}

    def request(method, url, params, json, headers, timeout):
        if calls['count'] == 0:
            calls['count'] += 1
            return DummyResponse(401, {})
        return DummyResponse(200, {'key': 'value'})
    monkeypatch.setattr(app.session, 'request', request)
    monkeypatch.setattr(app, 'refresh_access_token', lambda: True)
    st.session_state['access_token'] = 'tok'
    res = app.api_request('POST', '/path', params={'a': 1}, json_data={'b': 2})
    assert res == {'key': 'value'}


def test_api_request_error_detail_json(monkeypatch):
    monkeypatch.setattr(app.session, 'request', lambda m, u, params,
                        json, headers, timeout: DummyResponse(
                            400, {'detail': 'oops'}))
    called = {}
    monkeypatch.setattr(st, 'error', lambda msg: called.setdefault('msg', msg))
    assert app.api_request('GET', '/p') is None
    assert 'Error [400]: oops' in called['msg']


def test_api_request_error_text(monkeypatch):
    monkeypatch.setattr(app.session, 'request', lambda m, u, params, json,
                        headers, timeout: DummyResponse(
                            500, None, text='server err'))
    called = {}
    monkeypatch.setattr(st, 'error', lambda msg: called.setdefault('msg', msg))
    assert app.api_request('GET', '/p') is None
    # Implementation strips non-JSON detail, so message ends with colon/space
    assert called['msg'] == 'Error [500]: '

# fetch_books


@pytest.mark.parametrize("data,sort_order,expected_first", [
    ([{'download_count': 2}, {'download_count': 5}], 'Most downloaded', 5),
    ([{'download_count': 2}, {'download_count': 5}], 'Least downloaded', 2),
])
def test_fetch_books_parametrized(monkeypatch,
                                  data, sort_order, expected_first):
    app.fetch_books.clear()
    monkeypatch.setattr(app, 'api_request', lambda m, p,
                        params=None, json_data=None: data)
    result = app.fetch_books(1, '', sort_order)
    assert result[0]['download_count'] == expected_first
    monkeypatch.setattr(app, 'api_request', lambda m, p,
                        params=None, json_data=None: data)
    result = app.fetch_books(1, '', sort_order)
    assert result[0]['download_count'] == expected_first

# fetch_books


def test_fetch_books_search(monkeypatch):
    app.fetch_books.clear()
    monkeypatch.setattr(
        app, 'api_request', lambda m, p, params=None, json_data=None: [
                        {'download_count': 5}, {'download_count': 1}])
    res = app.fetch_books(1, 'q', 'Most downloaded')
    assert res[0]['download_count'] == 5
    monkeypatch.setattr(
        app, 'api_request', lambda m, p, params=None, json_data=None: [
                        {'download_count': 5}, {'download_count': 1}])
    res = app.fetch_books(1, 'q', 'Most downloaded')
    assert res[0]['download_count'] == 5


def test_fetch_books_no_search(monkeypatch):
    app.fetch_books.clear()
    monkeypatch.setattr(
        app, 'api_request', lambda m, p, params=None, json_data=None: [
                        {'download_count': 1}, {'download_count': 10}])
    res = app.fetch_books(1, '', 'Least downloaded')
    assert res[0]['download_count'] == 1
    monkeypatch.setattr(
        app, 'api_request', lambda m, p, params=None, json_data=None: [
                        {'download_count': 1}, {'download_count': 10}])
    res = app.fetch_books(1, '', 'Least downloaded')
    assert res[0]['download_count'] == 1

# fetch_book_details, fetch_favourites, fetch_reading_list


def test_fetch_book_details(monkeypatch):
    monkeypatch.setattr(app, 'api_request', lambda m, p,
                        params=None, json_data=None: {'id': 1})
    assert app.fetch_book_details(1) == {'id': 1}


def test_fetch_favourites(monkeypatch):
    app.fetch_favourites.clear()
    monkeypatch.setattr(app, 'api_request', lambda m, p, params=None,
                        json_data=None: {'favourites': [{'book_id': 1}]})
    assert app.fetch_favourites() == {'favourites': [{'book_id': 1}]}


def test_fetch_reading_list(monkeypatch):
    app.fetch_reading_list.clear()
    monkeypatch.setattr(
        app, 'api_request', lambda m, p, params=None, json_data=None: {
                        'reading_list': [{'book_id': 2}]})
    assert app.fetch_reading_list() == {'reading_list': [{'book_id': 2}]}

# login


def test_login_success(monkeypatch):
    monkeypatch.setattr(
        app.session, 'post', lambda u, json, timeout: DummyResponse(
            200, {'access_token': 'a', 'refresh_token': 'r', 'expires_in': 100}
            ))
    assert app.login('e', 'p') is True
    assert st.session_state['access_token'] == 'a'
    assert st.session_state['user_email'] == 'e'


def test_login_failure(monkeypatch):
    monkeypatch.setattr(app.session, 'post', lambda u, json,
                        timeout: DummyResponse(400, {'detail': 'no'}))
    called = {}
    monkeypatch.setattr(st, 'error', lambda msg: called.setdefault('msg', msg))
    assert app.login('e', 'p') is False
    assert 'Login failed' in called['msg']

# register


def test_register_success(monkeypatch):
    monkeypatch.setattr(app.session, 'post', lambda u,
                        json, timeout: DummyResponse(201))
    called = {}
    monkeypatch.setattr(
        st, 'success', lambda msg: called.setdefault('msg', msg))
    assert app.register('n', 's', 'e', 'p') is True
    assert 'Registration successful' in called['msg']


def test_register_failure(monkeypatch):
    monkeypatch.setattr(app.session, 'post', lambda u, json,
                        timeout: DummyResponse(400, {'detail': 'err'}))
    called = {}
    monkeypatch.setattr(st, 'error', lambda msg: called.setdefault('msg', msg))
    assert app.register('n', 's', 'e', 'p') is False
    assert 'Registration failed' in called['msg']

# logout


def test_logout(monkeypatch):
    st.session_state['refresh_token'] = 'rt'
    st.session_state['access_token'] = 'tok'
    monkeypatch.setattr(
        app.session, 'post', lambda u, json, headers, timeout: (
            _ for _ in ()).throw(requests.RequestException()))
    app.logout()
    assert st.session_state['access_token'] is None
    assert st.session_state['refresh_token'] is None
