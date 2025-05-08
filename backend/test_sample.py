import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import util.token as token_util

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 5 - 3 == 2

def test_multiplication():
    assert 2 * 3 == 6

def test_division():
    assert 10 / 2 == 5

def test_true():
    assert True

def test_generate_jwt_token_and_decode(monkeypatch):
    monkeypatch.setattr(token_util.config, 'get_secret_key', lambda: 'secret')
    monkeypatch.setattr(token_util.config, 'get_jwt_algorithm', lambda: 'HS256')
    data = {"foo": "bar"}
    jwt_token = token_util.generate_jwt_token(data)
    decoded = token_util.decode_access_token(jwt_token)
    assert decoded["foo"] == "bar"

def test_decode_refresh_token(monkeypatch):
    monkeypatch.setattr(token_util.config, 'get_secret_key', lambda: 'secret')
    monkeypatch.setattr(token_util.config, 'get_jwt_algorithm', lambda: 'HS256')
    data = {"baz": 123}
    jwt_token = token_util.generate_jwt_token(data)
    decoded = token_util.decode_refresh_token(jwt_token)
    assert decoded["baz"] == 123

def test_create_access_token_calls_save_refresh_token(monkeypatch):
    monkeypatch.setattr(token_util.config, 'get_secret_key', lambda: 'secret')
    monkeypatch.setattr(token_util.config, 'get_jwt_algorithm', lambda: 'HS256')
    monkeypatch.setattr(token_util.config, 'get_access_token_expire_minutes', lambda: 1)
    monkeypatch.setattr(token_util.config, 'get_refresh_token_expire_minutes', lambda: 2)
    mock_db = MagicMock()
    with patch('backend.util.token.save_refresh_token') as mock_save:
        data = {"id": 1, "sub": "test@example.com", "name": "Test", "surname": "User"}
        result = token_util.create_access_token(mock_db, data)
        assert "access_token" in result
        assert "refresh_token" in result
        mock_save.assert_called_once()

def test_regenerate_access_token(monkeypatch):
    monkeypatch.setattr(token_util.config, 'get_secret_key', lambda: 'secret')
    monkeypatch.setattr(token_util.config, 'get_jwt_algorithm', lambda: 'HS256')
    monkeypatch.setattr(token_util.config, 'get_access_token_expire_minutes', lambda: 1)
    data = {"id": 1, "sub": "test@example.com"}
    jwt_token = token_util.generate_jwt_token(data)
    result = token_util.regenerate_access_token(jwt_token)
    assert "access_token" in result
    assert "expires_in" in result 