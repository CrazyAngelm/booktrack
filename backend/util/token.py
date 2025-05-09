from datetime import timedelta, timezone, datetime

from jose import jwt
from sqlalchemy.orm import Session
from config import Config

from core.users import save_refresh_token


config = Config()


def generate_jwt_token(token_data: dict) -> str:
    return jwt.encode(
        token_data, config.get_secret_key(), 
        algorithm=config.get_jwt_algorithm()
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        jwt=token, key=config.get_secret_key(), 
        algorithms=[config.get_jwt_algorithm()]
    )


def decode_refresh_token(token: str) -> dict:
    return jwt.decode(
        token, config.get_secret_key(), algorithms=[config.get_jwt_algorithm()]
    )


def create_access_token(db: Session, data: dict):

    to_encode = data.copy()

    current_datetime = datetime.now(tz=timezone.utc)

    access_token_expires_in = (
        current_datetime + timedelta(minutes=config.get_access_token_expire_minutes())
    ).timestamp()

    refresh_token_expires_in = (
        current_datetime + timedelta(minutes=config.get_refresh_token_expire_minutes())
    ).timestamp()

    to_encode.update({"exp": access_token_expires_in})
    access_token = generate_jwt_token(to_encode)

    to_encode.update({"exp": refresh_token_expires_in})
    refresh_token = generate_jwt_token(to_encode)

    expires_at_datetime = datetime.fromtimestamp(refresh_token_expires_in)
    save_refresh_token(db, to_encode["id"], refresh_token, expires_at_datetime)

    return {
        "access_token": access_token,
        "expires_in": int(access_token_expires_in),
        "refresh_token": refresh_token,
        "refresh_token_expires_in": int(refresh_token_expires_in),
    }


def regenerate_access_token(refresh_token: str) -> dict:
    token_data = decode_refresh_token(refresh_token)
    current_datetime = datetime.now(tz=timezone.utc)
    access_token_expires_in = (
        current_datetime + timedelta(minutes=config.get_access_token_expire_minutes())
    ).timestamp()
    access_token = generate_jwt_token(token_data)
    return {
        "access_token": access_token, 
        "expires_in": int(access_token_expires_in)
    }
