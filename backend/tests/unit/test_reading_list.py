import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from datetime import datetime
from core.reading_list import *
from core.reading_list.models import ReadingListBook


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_reading_list_book():
    return ReadingListBook(
        user_email="user@example.com",
        book_id=1,
        status="want",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )


def test_get_reading_list_by_user_email(mock_db, mock_reading_list_book):
    mock_db.query.return_value.filter.return_value.all.return_value = [
        mock_reading_list_book]

    result = get_reading_list_by_user_email(mock_db, "user@example.com")

    assert result == [mock_reading_list_book]
    mock_db.query.return_value.filter.return_value.all.assert_called_once()


def test_get_reading_list_book_by_book_id(mock_db, mock_reading_list_book):
    mock_db.query.return_value.filter.return_value.\
        filter.return_value.first.return_value = mock_reading_list_book

    result = get_reading_list_book_by_book_id(mock_db, "user@example.com", 1)

    assert result == mock_reading_list_book
    mock_db.query.return_value.filter.return_value.\
        filter.return_value.first.assert_called_once()


def test_get_reading_list_by_status(mock_db, mock_reading_list_book):
    mock_db.query.return_value.filter.return_value.\
        filter.return_value.all.return_value = [
            mock_reading_list_book]

    result = get_reading_list_by_status(mock_db, "user@example.com", "want")

    assert result == [mock_reading_list_book]
    mock_db.query.return_value.filter.return_value.\
        filter.return_value.all.assert_called_once()


def test_create_reading_list_book(mock_db):
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result = create_reading_list_book(mock_db, "user@example.com", 1, "want")

    assert result.user_email == "user@example.com"
    assert result.book_id == 1
    assert result.status == "want"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_reading_list_book(mock_db, mock_reading_list_book):
    mock_db.query.return_value.filter.return_value.\
        filter.return_value.first.return_value = mock_reading_list_book

    result = update_reading_list_book(
        mock_db, "user@example.com", 1, "reading")

    assert result.status == "reading"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_delete_reading_list_book(mock_db, mock_reading_list_book):
    mock_db.query.return_value.filter.return_value.\
        filter.return_value.first.return_value = mock_reading_list_book

    result = delete_reading_list_book(mock_db, "user@example.com", 1)

    assert result == mock_reading_list_book
    mock_db.delete.assert_called_once_with(mock_reading_list_book)
    mock_db.commit.assert_called_once()
