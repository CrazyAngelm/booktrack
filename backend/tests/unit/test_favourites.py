import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from datetime import datetime
from core.favourites import *


@pytest.fixture
def mock_db():
    """Fixture for mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_favourite():
    """Fixture for creating a mock Favourite object"""
    return Favourite(
        user_email="test@example.com",
        book_id=1,
        created_at=datetime.datetime.now()
    )


def test_get_favourites_by_user_email(mock_db, mock_favourite):
    # Setup
    mock_db.query.return_value.filter.return_value.all.return_value = [
        mock_favourite]

    # Act
    result = get_favourites_by_user_email(mock_db, "test@example.com")

    # Assert
    assert len(result) == 1
    assert result[0].user_email == "test@example.com"
    mock_db.query.return_value.filter.return_value.all.assert_called_once()


def test_get_favourite_by_book_id(mock_db, mock_favourite):
    # Setup
    mock_query = mock_db.query.return_value
    mock_filter1 = mock_query.filter.return_value

    mock_filter2 = MagicMock()
    mock_filter2.first.return_value = mock_favourite

    mock_filter1.filter.return_value = mock_filter2
    # Act
    result = get_favourite_by_book_id(mock_db, "test@example.com", 1)

    # Assert
    assert result is mock_favourite
    assert result.user_email == "test@example.com"
    mock_filter2.first.assert_called_once()


def test_create_favourite(mock_db):
    # Setup
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    # Act
    result = create_favourite(mock_db, "test@example.com", 1)

    # Assert
    assert result.user_email == "test@example.com"
    assert result.book_id == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_favourite_create(mock_db, mock_favourite):
    # Setup
    # No existing favourite
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    update_favourite(mock_db, "test@example.com", 1, True)

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_update_favourite_delete(mock_db, mock_favourite):
    # Setup
    # Existing favourite
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_favourite

    # Act
    update_favourite(mock_db, "test@example.com", 1, False)

    # Assert
    mock_db.delete.assert_called_once()
    mock_db.commit.assert_called_once()


def test_update_favourite_no_action(mock_db, mock_favourite):
    # Setup
    # Existing favourite
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_favourite

    # Act
    # No action required, favourite remains
    update_favourite(mock_db, "test@example.com", 1, True)
    mock_db.delete.assert_not_called()
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
