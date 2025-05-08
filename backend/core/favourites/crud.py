from sqlalchemy.orm import Session
import datetime

from .models import Favourite


def get_favourites_by_user_email(db: Session, user_email: str) -> list[Favourite]:
    return db.query(Favourite).filter(Favourite.user_email == user_email).all()


def get_favourite_by_book_id(db: Session, user_email: str, book_id: int) -> Favourite | None:
    return db.query(Favourite).filter(Favourite.user_email == user_email).filter(Favourite.book_id == book_id).first()

def create_favourite(db: Session, user_email: str, book_id: int) -> Favourite:
    db_favourite = Favourite(
        user_email=user_email,
        book_id=book_id,
        created_at=datetime.datetime.now(),
    )

    db.add(db_favourite)
    db.commit()
    db.refresh(db_favourite)
    return db_favourite


def update_favourite(db: Session, user_email: str, book_id: int, is_favourite: bool) -> Favourite:
    db_favourite = db.query(Favourite).filter(
        Favourite.user_email == user_email,
        Favourite.book_id == book_id
    ).first()

    if db_favourite:
        if is_favourite == False:
            db.delete(db_favourite)
            db.commit()
    else:
        if is_favourite == True:
            db_favourite = create_favourite(db, user_email, book_id)
    
    print(f"Updated favourite for user {user_email} and book {book_id} to {is_favourite}")

    

