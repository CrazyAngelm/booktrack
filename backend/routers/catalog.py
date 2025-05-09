from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_user
from core.users import AuthenticatedUser
from core.catalog import BookRead
from services import CatalogService
catalog_router = APIRouter(tags=["Catalog"])
catalog_service = CatalogService()


@catalog_router.get(
    "/api/books",
    response_model=list[BookRead],
    summary="Paginated books",
    status_code=200,
)
def fetch_books_paginated_endpoint(
    page_no: int = 1,
    page_size: int = 36,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_user),
):
    results = catalog_service.fetch_books_paginated(db, page_no, page_size)
    if not results:
        raise HTTPException(status_code=404, detail="No books found")
    return results


@catalog_router.get(
    "/api/books/book-id/{book_id}",
    response_model=BookRead,
    summary="Get book by ID",
    status_code=200,
)
def fetch_book_by_id_endpoint(
    book_id: int,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_user),
):
    result = catalog_service.fetch_book_by_id(db, book_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return result


@catalog_router.get(
    "/api/books/search",
    response_model=list[BookRead],
    summary="Search books",
    status_code=200,
)
def search_books_endpoint(
    query: str,
    page_no: int = 1,
    page_size: int = 36,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_user),
):
    results = catalog_service.search_books(db, query, page_no, page_size)
    if not results:
        raise HTTPException(status_code=404, detail="No books found")
    return results
