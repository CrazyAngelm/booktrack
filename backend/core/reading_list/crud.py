from sqlalchemy.orm import Session
import datetime

from .models import ReadingListBook
from core.logging import audit_logger


def get_reading_list_by_user_email(db: Session, user_email: str) -> list[ReadingListBook]:
    return db.query(ReadingListBook).filter(ReadingListBook.user_email == user_email).all()


def get_reading_list_book_by_book_id(
        db: Session, 
        user_email: str, 
        book_id: int
) -> ReadingListBook | None:
    return db.query(ReadingListBook).filter(ReadingListBook.book_id == book_id) \
        .filter(ReadingListBook.user_email == user_email).first()


def get_reading_list_by_status(
        db: Session, 
        user_email: str, 
        status: str
) -> list[ReadingListBook]:
    return db.query(ReadingListBook).filter(ReadingListBook.user_email == user_email) \
        .filter(ReadingListBook.status == status).all()


def create_reading_list_book(
        db: Session, 
        user_email: str, 
        book_id: int, 
        status: str
) -> ReadingListBook:
    db_reading_list_book = ReadingListBook(
        user_email=user_email,
        book_id=book_id,
        status=status,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )

    db.add(db_reading_list_book)
    db.commit()
    db.refresh(db_reading_list_book)
    audit_logger.info(
        f"User {user_email} added book {book_id} to reading list with status {status}"
    )
    return db_reading_list_book


def update_reading_list_book(
        db: Session, 
        user_email: str, 
        book_id: int, 
        status: str
) -> ReadingListBook:
    db_reading_list_book = db.query(ReadingListBook) \
        .filter(ReadingListBook.user_email == user_email) \
        .filter(ReadingListBook.book_id == book_id).first()
    if db_reading_list_book:
        db_reading_list_book.status = status
        db_reading_list_book.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(db_reading_list_book)
        audit_logger.info(
            f"User {user_email} updated book {book_id} status to {status}"
        )
    return db_reading_list_book

    
def delete_reading_list_book(db: Session, user_email: str, book_id):
    db_reading_list_book = db.query(ReadingListBook) \
        .filter(ReadingListBook.user_email == user_email) \
        .filter(ReadingListBook.book_id == book_id).first()
    if db_reading_list_book:
        db.delete(db_reading_list_book)
        db.commit()
        audit_logger.info(
            f"User {user_email} deleted book {book_id} from reading list"
        )
    return db_reading_list_book
