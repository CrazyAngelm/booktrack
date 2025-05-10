import datetime
from unittest.mock import MagicMock
import pytest
from hypothesis import given, strategies as st
from sqlalchemy.orm import Session

from core.favourites import (
    get_favourites_by_user_email,
    get_favourite_by_book_id,
    create_favourite,
    update_favourite,
)
from core.favourites.models import Favourite

# Strategy for generating user emails
user_email_strategy = st.emails()

# Strategy for generating book IDs
book_id_strategy = st.integers(min_value=1, max_value=1_000_000)

# Strategy for generating Favourite instances
@st.composite
def favourite_strategy(draw):
    user_email = draw(user_email_strategy)
    book_id = draw(book_id_strategy)
    created_at = draw(st.datetimes(
        min_value=datetime.datetime(2000, 1, 1),
        max_value=datetime.datetime.now()
    ))
    return Favourite(
        user_email=user_email,
        book_id=book_id,
        created_at=created_at
    )

@given(user_email=user_email_strategy)
def test_get_favourites_by_user_email(user_email):
    db = MagicMock(spec=Session)
    mock_favourites = [Favourite(user_email=user_email, book_id=i, created_at=datetime.datetime.now()) for i in range(5)]
    db.query().filter().all.return_value = mock_favourites

    favourites = get_favourites_by_user_email(db, user_email)
    assert isinstance(favourites, list)
    for fav in favourites:
        assert isinstance(fav, Favourite)
        assert fav.user_email == user_email

@given(user_email=user_email_strategy, book_id=book_id_strategy)
def test_get_favourite_by_book_id(user_email, book_id):
    db = MagicMock(spec=Session)
    mock_favourite = Favourite(user_email=user_email, book_id=book_id, created_at=datetime.datetime.now())
    db.query().filter().filter().first.return_value = mock_favourite

    favourite = get_favourite_by_book_id(db, user_email, book_id)
    assert isinstance(favourite, Favourite)
    assert favourite.user_email == user_email
    assert favourite.book_id == book_id

@given(user_email=user_email_strategy, book_id=book_id_strategy)
def test_create_favourite(user_email, book_id):
    db = MagicMock(spec=Session)
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()

    favourite = create_favourite(db, user_email, book_id)
    assert isinstance(favourite, Favourite)
    assert favourite.user_email == user_email
    assert favourite.book_id == book_id
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(favourite)

@pytest.mark.parametrize("existing_fav, is_favourite, should_delete", [
    (True, False, True),   # Favourite exists and should be deleted
    (True, True, False),   # Favourite exists and should remain
    (False, False, False), # Favourite does not exist and should not be deleted
    (False, True, False),  # Favourite does not exist and should be created
])
def test_update_favourite(existing_fav, is_favourite, should_delete):
    db = MagicMock()
    user_email = "test@example.com"
    book_id = 123

    if existing_fav:
        fav = Favourite(user_email=user_email, book_id=book_id, created_at=datetime.datetime.now())
        db.query().filter().first.return_value = fav
    else:
        db.query().filter().first.return_value = None

    result = update_favourite(db, user_email, book_id, is_favourite)

    if should_delete:
        db.delete.assert_called_once_with(fav)
        db.commit.assert_called_once()
    else:
        db.delete.assert_not_called()