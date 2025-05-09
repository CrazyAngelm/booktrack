import datetime
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session, Query
import core.favourites.crud as crud_module
from core.favourites.crud import (
    get_favourites_by_user_email,
    get_favourite_by_book_id,
    create_favourite,
    update_favourite,
)
import core 
from core.favourites.models import Favourite

# ----------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------

@pytest.fixture
def mock_db():
    """A mocked SQLAlchemy Session."""
    return MagicMock(spec=Session)

@pytest.fixture
def sample_fav():
    """A sample Favourite instance."""
    return Favourite(
        user_email="alice@example.com",
        book_id=42,
        created_at=datetime.datetime(2025,1,1,12,0,0)
    )

# ----------------------------------------------------------------
# Tests for get_favourites_by_user_email
# ----------------------------------------------------------------

def test_get_favourites_by_user_email_calls_query_and_filter(mock_db, sample_fav):
    """
    Ensure get_favourites_by_user_email calls:
      1) db.query(Favourite)
      2) .filter(Favourite.user_email == email)
      3) .all()
    and returns its result.
    """
    # Arrange
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value.all.return_value = [sample_fav]

    # Act
    result = get_favourites_by_user_email(mock_db, "alice@example.com")

    # Assert query(Favourite) was called (kills mutant mutating Favourite→None) :contentReference[oaicite:0]{index=0}
    mock_db.query.assert_called_once_with(Favourite)

    # Assert that filter() was called exactly once with the correct equality expression :contentReference[oaicite:1]{index=1}
    assert mock_query.filter.call_count == 1
    expr = mock_query.filter.call_args_list[0][0][0]
    assert str(expr) == str(Favourite.user_email == "alice@example.com")

    # Assert .all() was called and result returned correctly
    mock_query.filter.return_value.all.assert_called_once()
    assert result == [sample_fav]

def test_get_favourites_by_user_email_empty(mock_db):
    """
    If there are no favourites for the email, .all() returns [].
    This kills mutants that invert or drop the filter. :contentReference[oaicite:2]{index=2}
    """
    mock_db.query.return_value.filter.return_value.all.return_value = []
    result = get_favourites_by_user_email(mock_db, "bob@example.com")
    assert result == []


# ----------------------------------------------------------------
# Tests for get_favourite_by_book_id
# ----------------------------------------------------------------

def test_get_favourite_by_book_id_calls_query_and_two_filters(mock_db, sample_fav):
    """
    Ensure get_favourite_by_book_id calls:
      1) db.query(Favourite)
      2) .filter(...) twice (user_email then book_id)
      3) .first()
    and returns its result.
    """
    # Arrange: set up the chain of filters returning our sample_fav
    mock_query = mock_db.query.return_value
    first_filter = mock_query.filter.return_value
    second_filter = first_filter.filter.return_value
    second_filter.first.return_value = sample_fav

    # Act
    result = get_favourite_by_book_id(mock_db, "alice@example.com", 42)

    # Assert the result is returned
    assert result is sample_fav

    # 1) db.query(Favourite) was called
    mock_db.query.assert_called_once_with(Favourite)

    # 2a) first .filter(...) was called on the query
    mock_query.filter.assert_called_once()

    # 2b) second .filter(...) was called on the first filter’s result
    first_filter.filter.assert_called_once()

    # 3) .first() was called on the second filter’s result
    second_filter.first.assert_called_once()


def test_get_favourite_by_book_id_filters_are_equal(mock_db, sample_fav):
    """
    New test: Ensure get_favourite_by_book_id uses the correct == filters
    (not !=) and queries Favourite, so mutants x2 and x3 are killed.
    """
    # Arrange: chain filters to return our sample_fav
    q = mock_db.query.return_value
    first_f = q.filter.return_value
    second_f = first_f.filter.return_value
    second_f.first.return_value = sample_fav

    # Act
    result = get_favourite_by_book_id(mock_db, "alice@example.com", 42)

    # Assert it returns our object
    assert result is sample_fav

    # 1) Must query the Favourite model
    mock_db.query.assert_called_once_with(Favourite)

    # 2) First filter must be on user_email == "alice@example.com"
    first_filter_expr = q.filter.call_args_list[0][0][0]
    assert str(first_filter_expr) == str(Favourite.user_email == "alice@example.com")

    # 3) Second filter must be on book_id == 42
    second_filter_expr = first_f.filter.call_args_list[0][0][0]
    assert str(second_filter_expr) == str(Favourite.book_id == 42)

    # 4) first() is invoked
    second_f.first.assert_called_once()
    
    
def test_create_favourite_sets_created_at_and_logs(monkeypatch, mock_db):
    """
    New test: Freeze datetime so we can assert created_at is exactly now(),
    killing the mutmut_5 that removes created_at.
    """
    # Freeze time
    fixed = datetime.datetime(2025, 1, 1, 0, 0, 0)
    class DummyDateTime:
        @classmethod
        def now(cls):
            return fixed
    monkeypatch.setattr("core.favourites.crud.datetime.datetime", DummyDateTime)

    # Capture logs
    logs = []
    class DummyLogger:
        def info(self, msg): logs.append(msg)
    monkeypatch.setattr(crud_module, "audit_logger", DummyLogger())

    # Act
    fav = create_favourite(mock_db, "bob@example.com", 99)

    # Assert created_at is our fixed time
    assert fav.created_at == fixed

    # Assert DB actions
    mock_db.add.assert_called_once_with(fav)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(fav)

    # Assert logging happened
    assert any("added book 99" in m for m in logs)

   
def test_update_favourite_filters_are_equal(mock_db, sample_fav):
    """
    New test: ensure the two‐argument filter in update_favourite uses
    == user_email and == book_id, killing mutmut_2 and mutmut_3.
    """
    # Arrange existing record so we go into the db_favourite branch
    mock_db.query.return_value\
        .filter.return_value\
        .filter.return_value.first.return_value = sample_fav

    # Act
    update_favourite(mock_db, "dave@example.com", 555, False)

    # Assert the combined filter call uses two correct args,
    # rather than inverted ones:
    called_args = mock_db.query.return_value.filter.call_args[0]
    # This filter takes two positional expressions:
    exprs = set(str(e) for e in called_args)
    assert str(Favourite.user_email == "dave@example.com") in exprs
    assert str(Favourite.book_id == 555) in exprs

    # And delete/commit happen
    mock_db.delete.assert_called_once()
    mock_db.commit.assert_called_once()
    

def test_get_favourite_by_book_id_not_found(mock_db):
    """
    If no matching favourite exists, .first() returns None.
    This tests the path where the method should return None :contentReference[oaicite:4]{index=4}
    """
    mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = None
    result = get_favourite_by_book_id(mock_db, "alice@example.com", 99)
    assert result is None


# ----------------------------------------------------------------
# Tests for create_favourite
# ----------------------------------------------------------------

def test_create_favourite_adds_and_commits_and_logs(monkeypatch, mock_db):
    """
    Verify create_favourite:
      - constructs a Favourite with correct attributes
      - calls add(), commit(), refresh()
      - logs the audit message
    """
    # Capture logs
    messages = []
    class DummyLogger:
        def info(self, msg): messages.append(msg)
    monkeypatch.setattr("core.favourites.crud.audit_logger", DummyLogger())

    # Act
    fav = create_favourite(mock_db, "carol@example.com", 7)

    # Assert correct instance returned
    assert isinstance(fav, Favourite)
    assert fav.user_email == "carol@example.com"
    assert fav.book_id == 7
    # SQLAlchemy calls
    mock_db.add.assert_called_once_with(fav)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(fav)
    # Audit log
    assert "User carol@example.com added book 7 to favourites." in messages


# ----------------------------------------------------------------
# Tests for update_favourite
# ----------------------------------------------------------------

def test_update_favourite_removes_existing(mock_db, sample_fav, monkeypatch):
    """
    When is_favourite=False and record exists,
    delete() and commit() should be called and logged. :contentReference[oaicite:5]{index=5}
    """
    # Mock existing record
    mock_q = mock_db.query.return_value
    mock_q.filter.return_value.first.return_value = sample_fav

    # Capture logs
    messages = []
    class DummyLogger:
        def info(self, msg): messages.append(msg)
    monkeypatch.setattr(crud_module, "audit_logger", DummyLogger())

    # Act
    update_favourite(mock_db, "alice@example.com", 42, False)

    # Assert
    mock_db.delete.assert_called_once_with(sample_fav)
    mock_db.commit.assert_called_once()
    assert "removed book 42" in messages[0]

def test_update_favourite_creates_when_missing(mock_db, monkeypatch):
    """
    When is_favourite=True and no record exists,
    create_favourite should be called and logged. :contentReference[oaicite:6]{index=6}
    """
    # Ensure no existing record
    mock_q = mock_db.query.return_value
    mock_q.filter.return_value.first.return_value = None

    # Spy on create_favourite
    created = MagicMock(return_value=sample_fav)
    monkeypatch.setattr("core.favourites.crud.create_favourite", created)

    # Capture logs
    messages = []
    class DummyLogger:
        def info(self, msg): messages.append(msg)
    monkeypatch.setattr(crud_module, "audit_logger", DummyLogger())

    # Act
    update_favourite(mock_db, "user@example.com", 99, True)

    # Assert
    created.assert_called_once_with(mock_db, "user@example.com", 99)
    assert any("added book 99" in m for m in messages)

def test_update_favourite_noop_when_already_favourite(mock_db, sample_fav):
    """
    When is_favourite=True and record exists,
    neither delete() nor create() should be called. :contentReference[oaicite:7]{index=7}
    """
    mock_q = mock_db.query.return_value
    mock_q.filter.return_value.first.return_value = sample_fav

    # Act
    update_favourite(mock_db, "alice@example.com", 42, True)

    # Assert no DML executed
    mock_db.delete.assert_not_called()
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
