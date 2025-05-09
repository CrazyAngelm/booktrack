from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from core.catalog import Book


CACHE_TTL = timedelta(hours=1)


def get_books_by_page(db: Session, page: int) -> List[Book]:
    return db.query(Book).filter(Book.page == page).all()


def delete_books_by_page(db: Session, page: int):
    db.query(Book).filter(Book.page == page).delete(synchronize_session=False)
    db.commit()


def get_book_by_id(db: Session, book_id: int) -> Book | None:
    return db.query(Book).filter(Book.id == book_id).first()


def create_books(db: Session, page: int, books_data: List[dict]):
    objs = []
    now = datetime.now()
    for data in books_data:
        # Check if the book already exists
        existing_book = db.query(Book).filter(Book.id == data["id"]) \
            .filter(Book.page == page).first()
        if existing_book:
            continue  # Skip if the book already exists
        b = Book(
            id=data["id"],
            page=page,
            fetched_at=now,
            title=data["title"],
            subjects=data["subjects"],
            authors=[a for a in data["authors"]],
            summaries=data["summaries"],
            translators=[t for t in data["translators"]],
            languages=data["languages"],
            copyright=data.get("copyright"),
            media_type=data["media_type"],
            formats=data["formats"],
            download_count=data["download_count"],
        )
        objs.append(b)
    db.bulk_save_objects(objs)
    db.commit()
    return objs


def is_fresh(book: Book) -> bool:
    return (datetime.now() - book.fetched_at) < CACHE_TTL
