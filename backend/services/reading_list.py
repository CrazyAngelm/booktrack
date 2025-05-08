from sqlalchemy.orm import Session
from core.reading_list import ReadingListBook
from core.reading_list import get_reading_list_by_user_email, get_reading_list_book_by_book_id, get_reading_list_by_status, create_reading_list_book, update_reading_list_book, delete_reading_list_book


from config import Config

class ReadingListService():
    config = Config()
    
    def fetch_reading_list(self, user_email: str, db: Session) -> list[ReadingListBook]:
        """
        Fetches books from the database with pagination.
        """
        response = get_reading_list_by_user_email(db, user_email)
        if response:
            return response
        else:
            return []
    
    def fetch_reading_list_by_status(self, user_email: str, status: str, db: Session) -> list[ReadingListBook]:
        """
        Fetches books from the database with pagination.
        """
        response = get_reading_list_by_status(db, user_email, status)
        if response:
            return response
        else:
            return []
        
    def fetch_reading_list_book_for_user(self, user_email: str, book_id: int, db: Session) -> ReadingListBook | None:
        """
        Fetches a reading list book for the user from the database.
        """
        response = get_reading_list_book_by_book_id(db, user_email, book_id)
        if response:
            return response
        else:
            return None
        
    def create_reading_list_book_for_user(self, user_email: str, book_id: int, status: str, db: Session) -> ReadingListBook | None:
        """
        Creates a reading list book for the user in the database.
        """
        response = create_reading_list_book(db, user_email, book_id, status)
        if response:
            return response
        else:
            return None
        
    def update_reading_list_book_for_user(self, user_email: str, book_id: int, status: str, db: Session) -> ReadingListBook | None:
        """
        Updates the reading list book for the user in the database.
        """
        response = update_reading_list_book(db, user_email, book_id, status)
        if response:
            return response
        else:
            return None
    
    def delete_reading_list_book_for_user(self, user_email: str, book_id: int, db: Session) -> ReadingListBook | None:
        """
        Deletes the reading list book for the user in the database.
        """
        response = delete_reading_list_book(db, user_email, book_id)
        if response:
            return response
        else:
            return None