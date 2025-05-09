import requests
from datetime import datetime
from sqlalchemy.orm import Session

from config import Config
from core.catalog import Book
from core.catalog import (
    get_books_by_page,
    get_book_by_id,
    create_books,
    delete_books_by_page,
    is_fresh
)


class CatalogService:
    def __init__(self):
        self.config = Config()

    def fetch_books_paginated(
        self, db: Session, page_no: int, page_size: int
    ):
        # 1) Try the cache
        cached = get_books_by_page(db, page_no)
        if cached and all(is_fresh(b) for b in cached):
            # return as list of dicts
            return [self._to_dict(b) for b in cached]

        # 2) stale or missing → re-fetch
        url = f"{self.config.get_gutendex_base_url()}/books"
        params = {"page": page_no}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        payload = resp.json()

        # clear old page
        delete_books_by_page(db, page_no)
        # write new
        create_books(db, page_no, payload["results"])

        # return fresh
        return payload["results"]

    def fetch_book_by_id(self, db: Session, book_id: int):
        # 1) Cache
        book = get_book_by_id(db, book_id)
        if book and is_fresh(book):
            return self._to_dict(book)

        # 2) Re-fetch that single ID
        url = f"{self.config.get_gutendex_base_url()}/books"
        params = {"ids": book_id}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        payload = resp.json().get("results") or []
        if not payload or len(payload) == 0:
            return None

        # upsert into DB
        create_books(db, page=0, books_data=payload)
        return payload[0]

    def search_books(
        self, db: Session, query: str, page_no: int, page_size: int
    ):
        url = f"{self.config.get_gutendex_base_url()}/books"
        params = {"search": query, "page": page_no}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("results", [])

    def _to_dict(self, book: Book) -> dict:
        # strip SQLAlchemy obj into JSON-ready dict
        return {
            "id": book.id,
            "title": book.title,
            "subjects": book.subjects,
            "authors": book.authors,
            "summaries": book.summaries,
            "translators": book.translators,
            "languages": book.languages,
            "copyright": book.copyright,
            "media_type": book.media_type,
            "formats": book.formats,
            "download_count": book.download_count,
        }
