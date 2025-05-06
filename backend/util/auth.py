from jose import JWTError, jwt
from fastapi.exceptions import HTTPException
from fastapi import status

from core.users import AuthenticatedUser
from config import Config

config = Config()


def get_user_from_token(token: str):
    try:
        payload = jwt.decode(
            token, config.get_secret_key(), algorithms=[config.get_jwt_algorithm()]
        )
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        payload["email"] = payload.pop("sub")
        payload["has_logged_in"] = True
        return AuthenticatedUser(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(detail="Token has expired", status_code=401)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )