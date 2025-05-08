from sqlalchemy.orm import Session
import datetime

from .models import ReadingListBook


def get_reading_list_by_user_email(db: Session, user_email: str) -> list[ReadingListBook]:
    return db.query(ReadingListBook).filter(ReadingListBook.user_email == user_email).all()


def get_reading_list_book_by_book_id(db: Session, user_email: str, book_id: int) -> ReadingListBook | None:
    return db.query(ReadingListBook).filter(ReadingListBook.book_id == book_id).filter(ReadingListBook.user_email == user_email).first()

def get_reading_list_by_status(db: Session, user_email: str, status: str) -> list[ReadingListBook]:
    return db.query(ReadingListBook).filter(ReadingListBook.user_email == user_email).filter(ReadingListBook.status == status).all()


def create_reading_list_book(db: Session, user_email: str, book_id: int, status: str) -> ReadingListBook:
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
    return db_reading_list_book


def update_reading_list_book(db: Session, user_email: str, book_id: int, status: str) -> ReadingListBook:
    db_reading_list_book = db.query(ReadingListBook).filter(ReadingListBook.user_email == user_email).filter(ReadingListBook.book_id == book_id).first()
    if db_reading_list_book:
        db_reading_list_book.status = status
        db_reading_list_book.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(db_reading_list_book)
    return db_reading_list_book

    

