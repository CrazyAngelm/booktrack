import requests
from sqlalchemy.orm import Session
from core.favourites import Favourite
from core.favourites import (
    get_favourites_by_user_email, 
    get_favourite_by_book_id, 
    create_favourite, 
    update_favourite
)


from config import Config


class FavouritesService():
    config = Config()
    
    def fetch_favourites(
            self, 
            user_email: str, 
            db: Session
    ) -> list[Favourite]:
        """
        Fetches books from the database with pagination.
        """
        response = get_favourites_by_user_email(db, user_email)
        if response:
            return response
        else:
            return []
        
    def fetch_favourite_for_user(
            self, 
            user_email: str, 
            book_id: int, 
            db: Session
    ) -> Favourite | None:
        """
        Fetches a favourite for the user from the database.
        """
        response = get_favourite_by_book_id(db, user_email, book_id)
        if response:
            return response
        else:
            return None
        
    def create_favourite_for_user(
            self, 
            user_email: str, 
            book_id: int, 
            db: Session
    ) -> Favourite | None:
        """
        Creates a favourite for the user in the database.
        """
        response = create_favourite(db, user_email, book_id)
        if response:
            return response
        else:
            return None
        
    def update_favourite_for_user(
            self, 
            user_email: str, 
            book_id: int, 
            is_favourite: bool, 
            db: Session
    ) -> Favourite | None:
        """
        Updates the favourite for the user in the database.
        """
        update_favourite(db, user_email, book_id, is_favourite)
