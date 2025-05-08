from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_user
from core.users import AuthenticatedUser
from core.catalog import BookRead
from services import CatalogService
from config import Config


catalog_router = APIRouter(tags=["Catalog"])

catalog_service = CatalogService()
config = Config()


@catalog_router.get("/api/books", response_model=list[BookRead], status_code=200)
def fetch_books_paginated_endpoint(
    page_no: int = 1,
    page_size: int = 36,
    user: AuthenticatedUser = Depends(get_user)
):
    # TODO: Allow for page_size =! 36
    result = catalog_service.fetch_books_paginated(page_no=page_no, page_size=page_size)
    if not result:
        raise HTTPException(status_code=404, detail="No books found")
    return result.get("results", [])


@catalog_router.get("/api/books/book-id/{book_id}", response_model=BookRead, status_code=200)
def fetch_book_by_id_endpoint(
    book_id: int,
    user: AuthenticatedUser = Depends(get_user)
):
    result = catalog_service.fetch_book_by_id(book_id)
    if (not result) or (not result.get("results")) or (len(result.get("results")) == 0):
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return result.get("results")[0]


@catalog_router.get("/api/books/search", response_model=list[BookRead], status_code=200)
def search_books_endpoint(
    query: str,
    page_no: int = 1,
    page_size: int = 36,
    user: AuthenticatedUser = Depends(get_user)
):
    result = catalog_service.search_books(query=query, page_no=page_no, page_size=page_size)
    if not result:
        raise HTTPException(status_code=404, detail="No books found")
    return result.get("results", [])