from hypothesis import given, strategies as st
from sqlalchemy.orm import Session
import pytest
from unittest.mock import MagicMock
from core.catalog import *
from typing import List


@given(page=st.integers(min_value=0))
def test_get_books_by_page(page: int):
    # Create a MagicMock for the database session
    db = MagicMock(spec=Session)

    # Mock the query().filter().all() chain to return a list of Book objects
    mock_books = [Book(id=1, title="Test Book", page=page, subjects=[], authors=[], summaries=[], translators=[], languages=[], copyright=None, media_type="e-book", formats=["pdf"], download_count=0)]
    db.query().filter().all.return_value = mock_books

    # Call the function under test
    books = get_books_by_page(db, page)

    # Assert that the result is a list
    assert isinstance(books, list)
    if books:
        # Further check that the items in the list are instances of Book
        assert all(isinstance(book, Book) for book in books)

@given(page=st.integers(min_value=0))
def test_delete_books_by_page(page: int):
    db = MagicMock(spec=Session)
    try:
        delete_books_by_page(db, page)
    except Exception as e:
        pytest.fail(f"delete_books_by_page raised an exception: {e}")
        
        
@given(book_id=st.integers(min_value=0))
def test_get_book_by_id(book_id: int):
    # Create a MagicMock for the database session
    db = MagicMock(spec=Session)

    # Mock the query().filter().first() chain to return a Book object
    mock_book = Book(id=book_id, title="Test Book", page=1, subjects=[], authors=[], summaries=[], translators=[], languages=[], copyright=None, media_type="e-book", formats=["pdf"], download_count=0)
    db.query().filter().first.return_value = mock_book

    # Call the function under test
    book = get_book_by_id(db, book_id)

    # Assert that the result is an instance of Book
    if book:
        assert isinstance(book, Book)
        
@given(
    page=st.integers(min_value=0),
    books_data=st.lists(
        st.fixed_dictionaries({
            "id": st.integers(min_value=0),
            "title": st.text(),
            "subjects": st.lists(st.text()),
            "authors": st.lists(st.text()),
            "summaries": st.lists(st.text()),
            "translators": st.lists(st.text()),
            "languages": st.lists(st.text()),
            "copyright": st.text(),
            "media_type": st.text(),
            "formats": st.lists(st.text()),
            "download_count": st.integers(min_value=0),
        })
    )
)
def test_create_books(page: int, books_data: list):
    try:
        db = MagicMock(spec=Session)
        books = create_books(db, page, books_data)
        assert isinstance(books, list)
        if books:
            assert all(isinstance(book, Book) for book in books)
    except Exception as e:
        pytest.fail(f"create_books raised an exception: {e}")