import requests

from config import Config


class CatalogService():
    config = Config()
    
    def fetch_books_paginated(self, page_no: int, page_size: int):
        """
        Fetches books from the database with pagination.
        """
        url = self.config.get_gutendex_base_url() + "/books"
        params = {
            "page": page_no
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    def fetch_book_by_id(self, book_id: int):
        """
        Fetches a book by its ID from the database.
        """
        url = self.config.get_gutendex_base_url() + "/books"
        params = {
            "ids": book_id
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    def search_books(self, query: str, page_no: int, page_size: int):
        """
        Searches for books in the database.
        """
        url = self.config.get_gutendex_base_url() + "/books"
        params = {
            "search": query,
            "page": page_no
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
