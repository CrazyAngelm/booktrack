from core.users import UserCreate, LoginRequest
from sqlalchemy.orm import Session

from util import register, login, logout, regenerate_access_token


class UsersService():
    def register_user(self, user: UserCreate, db: Session):
        # Logic to register a user
        access_token = register(user, db)
        return access_token

    def login_user(self, request: LoginRequest, db: Session):
        # Logic to log in a user
        access_token = login(request, db)
        return access_token

    def logout_user(self, db: Session, refresh_token: str):
        # Logic to log out a user
        return logout(db, refresh_token)
        
    def regenerate_access_token_from_token(self, refresh_token: str):
        # Logic to regenerate access token
        return regenerate_access_token(refresh_token)
