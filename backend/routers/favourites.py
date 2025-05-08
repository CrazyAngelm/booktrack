from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_user
from core.users import AuthenticatedUser
from core.favourites import FavouriteRead
from services import FavouritesService
from config import Config


favourites_router = APIRouter(tags=["Favourites"])

favourites_service = FavouritesService()
config = Config()


@favourites_router.get("/api/favourites", response_model=dict[str, str | list[FavouriteRead]], status_code=200)
def fetch_favourites_for_user_endpoint(
    user: AuthenticatedUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    result = favourites_service.fetch_favourites(user.email, db)
    return {"user_email": user.email, "favourites": result}


@favourites_router.post("/api/favourites", response_model=FavouriteRead, status_code=201)
def create_favourite_endpoint(
    book_id: int,
    user: AuthenticatedUser = Depends(get_user),
    db: Session = Depends(get_db)
):
    result = favourites_service.create_favourite_for_user(user.email, book_id, db)
    if not result:
        raise HTTPException(status_code=401, detail="Failed to create favourite")
    return result

@favourites_router.patch("/api/favourites", response_model=dict, status_code=200)
def update_favourite_endpoint(
    book_id: int,
    is_favourite: bool,
    user: AuthenticatedUser = Depends(get_user),
    db: Session = Depends(get_db)
):
    try:
        favourites_service.update_favourite_for_user(user.email, book_id, is_favourite, db)
        return {"message": "Favourite updated successfully", "book_id": book_id, "user_email": user.email, "is_favourite": is_favourite}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Failed to update favourite: {str(e)}")
    