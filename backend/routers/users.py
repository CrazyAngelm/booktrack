import jwt
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, Body
from sqlalchemy.orm import Session
from dependencies import get_db, get_user

from core.users import UserCreate, LoginRequest, AccessToken, AuthenticatedUser
from core.users import get_refresh_token_by_user_id, get_refresh_token
from services import UsersService


users_router = APIRouter(tags=["Users"])

users_service = UsersService()


@users_router.post("/api/register/")
def register_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return users_service.register_user(user, db)


@users_router.post("/api/login")
def login_endpoint(request: LoginRequest, db: Session = Depends(get_db)):
    return users_service.login_user(request, db)


@users_router.post("/api/logout")
def logout_endpoint(
    refresh_token: Annotated[str, Body(embed=True)], 
    db: Session = Depends(get_db)
):
    return users_service.logout_user(db, refresh_token)


@users_router.post("/api/refresh-token", response_model=AccessToken)
def regenerate_access_token_endpoint(
    refresh_token: Annotated[str, Body(embed=True)], 
    db: Session = Depends(get_db)
):
    try:
        res = get_refresh_token(db, refresh_token)
        if res is None:
            raise HTTPException(
                detail="Invalid refresh token", 
                status_code=400
            )

        return users_service.regenerate_access_token_from_token(refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(detail="Token has expired", status_code=400)
    except jwt.InvalidTokenError:
        raise HTTPException(detail="Invalid refresh token", status_code=400)


@users_router.get("/api/get_token", include_in_schema=False)
def get_token_endpoint(
    user: AuthenticatedUser = Depends(get_user), db: Session = Depends(get_db)
):
    refresh_token = get_refresh_token_by_user_id(db, user.id)
    if not refresh_token:
        raise HTTPException(
            status_code=404, detail="Refresh token not found for the user"
        )
    return refresh_token
