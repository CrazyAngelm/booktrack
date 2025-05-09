from sqlalchemy.orm import Session
import datetime

from core.logging import audit_logger
from .models import Favourite


def get_favourites_by_user_email(db: Session, user_email: str) -> list[Favourite]:
    return db.query(Favourite).filter(Favourite.user_email == user_email).all()


def get_favourite_by_book_id(db: Session, user_email: str, book_id: int) -> Favourite | None:
    return db.query(Favourite).filter(Favourite.user_email == user_email) \
        .filter(Favourite.book_id == book_id).first()


def create_favourite(db: Session, user_email: str, book_id: int) -> Favourite:
    db_favourite = Favourite(
        user_email=user_email,
        book_id=book_id,
        created_at=datetime.datetime.now(),
    )

    db.add(db_favourite)
    db.commit()
    db.refresh(db_favourite)
    audit_logger.info(f"User {user_email} added book {book_id} to favourites.")
    return db_favourite


def update_favourite(db: Session, user_email: str, book_id: int, is_favourite: bool) -> Favourite:
    db_favourite = db.query(Favourite).filter(
        Favourite.user_email == user_email,
        Favourite.book_id == book_id
    ).first()

    if db_favourite:
        if not is_favourite:
            db.delete(db_favourite)
            db.commit()
            audit_logger.info(f"User {user_email} removed book {book_id} from favourites.")
    else:
        if is_favourite:
            db_favourite = create_favourite(db, user_email, book_id)
            audit_logger.info(f"User {user_email} added book {book_id} to favourites.")
    
