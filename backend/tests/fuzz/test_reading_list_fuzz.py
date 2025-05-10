import datetime
from unittest.mock import MagicMock
import pytest
from mock_alchemy.mocking import AlchemyMagicMock, UnifiedAlchemyMagicMock
from mock_alchemy.comparison import ExpressionMatcher
from hypothesis import given, strategies as st
from core.reading_list.models import ReadingListBook
from core.reading_list import crud

# Strategy for generating user emails
# Define strategies for generating test data
user_email_strategy = st.emails()
book_id_strategy = st.integers(min_value=1, max_value=10000)
status_strategy = st.sampled_from(["Read", "Reading", "Want"])

@given(user_email=user_email_strategy)
def test_get_reading_list_by_user_email(user_email):
    db = AlchemyMagicMock()
    crud.get_reading_list_by_user_email(db, user_email)
    db.query.return_value.filter.assert_called_once_with(ReadingListBook.user_email == user_email)


@given(user_email=user_email_strategy, book_id=book_id_strategy)
def test_get_reading_list_book_by_book_id(user_email, book_id):
    db = AlchemyMagicMock()
    crud.get_reading_list_book_by_book_id(db, user_email, book_id)
    db.query.assert_called_once_with(ReadingListBook)
    db.query.return_value.filter.assert_any_call(ReadingListBook.book_id == book_id)
    db.query.return_value.filter.return_value.filter.assert_any_call(ReadingListBook.user_email == user_email)
    db.query.return_value.filter.return_value.filter.return_value.first.assert_called_once()
    
    
@given(user_email=user_email_strategy, status=status_strategy)
def test_get_reading_list_by_status(user_email, status):
    db = AlchemyMagicMock()
    crud.get_reading_list_by_status(db, user_email, status)
    db.query.return_value.filter.return_value.filter.assert_called_once_with(ReadingListBook.status == status)
    

@given(user_email=user_email_strategy, book_id=book_id_strategy, status=status_strategy)
def test_create_reading_list_book(user_email, book_id, status):
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    result = crud.create_reading_list_book(db, user_email, book_id, status)
    assert isinstance(result, ReadingListBook)
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)

@given(user_email=user_email_strategy, book_id=book_id_strategy, status=status_strategy)
def test_update_reading_list_book(user_email, book_id, status):
    db = MagicMock()
    existing_book = ReadingListBook(
        user_email=user_email,
        book_id=book_id,
        status="to-read",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    db.query().filter().filter().first.return_value = existing_book
    result = crud.update_reading_list_book(db, user_email, book_id, status)
    assert result.status == status
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(existing_book)

@given(user_email=user_email_strategy, book_id=book_id_strategy)
def test_delete_reading_list_book(user_email, book_id):
    db = MagicMock()
    existing_book = ReadingListBook(
        user_email=user_email,
        book_id=book_id,
        status="to-read",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    db.query().filter().filter().first.return_value = existing_book
    result = crud.delete_reading_list_book(db, user_email, book_id)
    assert result == existing_book
    db.delete.assert_called_once_with(existing_book)
    db.commit.assert_called_once()
