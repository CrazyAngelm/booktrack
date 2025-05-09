import bcrypt

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from core.users import User
from core.users import LoginRequest, UserCreate
from core.users import get_user_by_email, get_refresh_token

from .token import create_access_token


def login(request: LoginRequest, db: Session):
    user_email = request.email
    user_password = request.password
    user = get_user_by_email(db, email=user_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    hashed_password = user.password.encode()
    provided_password = user_password.encode()

    if not bcrypt.checkpw(provided_password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return create_access_token(
        db,
        data={
            "sub": user.email,
            "id": str(user.id),
            "name": user.name,
            "surname": user.surname,
        },
    )


def register(user: UserCreate, db: Session):
    db_user_email = get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(
            status_code=409, 
            detail="The email is already registered"
        )

    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(user.password.encode(), salt).decode()
    new_user = User(
        name=user.name,
        surname=user.surname,
        email=user.email,
        password=hashed_password,
        salt=salt.decode(),
    )
    db.add(new_user)
    db.commit()
    return create_access_token(
        db,
        data={
            "sub": new_user.email,
            "id": str(new_user.id),
            "name": new_user.name,
            "surname": new_user.surname,
        },
    )


def logout(db: Session, refresh_token: str):
    res = get_refresh_token(db, refresh_token)
    if res is None:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    db.delete(res)
    db.commit()

    return {"detail": "Successfully logged out"}
