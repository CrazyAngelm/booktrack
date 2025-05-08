from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_user
from core.users import AuthenticatedUser
from core.reading_list import ReadingListBookRead
from services import ReadingListService
from config import Config


reading_list_router = APIRouter(tags=["Reading List"])

reading_list_service = ReadingListService()
config = Config()


@reading_list_router.get("/api/reading-list", response_model=dict[str, str | list[ReadingListBookRead]], status_code=200)
def fetch_favourites_for_user_endpoint(
    user: AuthenticatedUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    result = reading_list_service.fetch_reading_list(user.email, db)
    return {"user_email": user.email, "reading_list": result}


@reading_list_router.get("/api/reading-list/book-id/{book_id}", response_model=ReadingListBookRead, status_code=200)
def fetch_favourites_for_user_by_book_id_endpoint(
    book_id: int,
    user: AuthenticatedUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    # Check if book exists
    existing_book = reading_list_service.fetch_reading_list_book_for_user(user.email, book_id, db)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found in the reading list")
    return existing_book

@reading_list_router.get("/api/reading-list/status/{status}", response_model=dict[str, str | list[ReadingListBookRead]], status_code=200)
def fetch_favourites_for_user_by_status_endpoint(
    status: str,
    user: AuthenticatedUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    # Check if status is valid
    if status not in ["Want", "Reading", "Read"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    result = reading_list_service.fetch_reading_list_by_status(user.email, status, db)
    return {"user_email": user.email, "reading_list": result}


@reading_list_router.put("/api/reading-list/book-id/{book_id}", response_model=ReadingListBookRead, status_code=200)
def update_book_in_reading_list_endpoint(
    book_id: int,
    status: str,
    user: AuthenticatedUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    # Check if status is valid
    if status not in ["Want", "Reading", "Read"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    # Check if book exists
    existing_book = reading_list_service.fetch_reading_list_book_for_user(user.email, book_id, db)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found in the reading list")
    result = reading_list_service.update_reading_list_book_for_user(user.email, book_id, status, db)
    if not result:
        raise HTTPException(status_code=401, detail="Book was not updated successfully")
    return result


@reading_list_router.post("/api/reading-list", response_model=ReadingListBookRead, status_code=201)
def add_book_to_reading_list_endpoint(
    book_id: int,
    status: str,
    user: AuthenticatedUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    # Check if status is valid
    if status not in ["Want", "Reading", "Read"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    # Check duplicate
    existing_book = reading_list_service.fetch_reading_list_book_for_user(user.email, book_id, db)
    if existing_book:
        raise HTTPException(status_code=400, detail="Book already exists in the reading list")
    result = reading_list_service.create_reading_list_book_for_user(user.email, book_id, status, db)
    if not result:
        raise HTTPException(status_code=401, detail="Book was not added successfully")
    return result


@reading_list_router.delete("/api/reading-list/book-id/{book_id}", response_model=ReadingListBookRead, status_code=200)
def delete_book_from_reading_list_endpoint(
    book_id: int,
    user: AuthenticatedUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    # Check if book exists
    existing_book = reading_list_service.fetch_reading_list_book_for_user(user.email, book_id, db)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found in the reading list")
    result = reading_list_service.delete_reading_list_book_for_user(user.email, book_id, db)
    if not result:
        raise HTTPException(status_code=401, detail="Book was not deleted successfully")
    return result