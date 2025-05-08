import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from core.users.models import User, RefreshToken
from core.users import *  # Adjust to your actual import path
import uuid


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_user():
    return User(id=uuid.uuid4(), email="test@example.com", salt="somesalt")


@pytest.fixture
def mock_refresh_token():
    return RefreshToken(
        user_id=uuid.uuid4(),
        refresh_tokens="token123",
        expires_at="2025-12-31T23:59:59"
    )


def test_get_user_by_email(mock_db, mock_user):
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    result = get_user_by_email(mock_db, "test@example.com")

    assert result == mock_user
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_salt(mock_user):
    result = get_salt(mock_user)

    assert result == "somesalt"


def test_save_refresh_token_creates_new(mock_db):
    user_id = uuid.uuid4()
    token = "new_token"
    expires = "2025-12-31T23:59:59"
    mock_db.query.return_value.filter.return_value.first.return_value = None

    save_refresh_token(mock_db, str(user_id), token, expires)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_save_refresh_token_updates_existing(mock_db, mock_refresh_token):
    user_id = str(mock_refresh_token.user_id)
    token = "updated_token"
    expires = "2026-01-01T00:00:00"

    mock_db.query.return_value.filter.return_value.first.return_value = mock_refresh_token

    save_refresh_token(mock_db, user_id, token, expires)

    assert mock_refresh_token.refresh_tokens == token
    assert mock_refresh_token.expires_at == expires
    mock_db.add.assert_not_called()
    mock_db.commit.assert_called_once()


def test_get_refresh_token_by_user_id_found(mock_db, mock_refresh_token):
    mock_db.query.return_value.filter.return_value.first.return_value = mock_refresh_token

    result = get_refresh_token_by_user_id(mock_db, mock_refresh_token.user_id)

    assert result == mock_refresh_token


def test_get_refresh_token_by_user_id_not_found(mock_db):
    mock_db.query.return_value
