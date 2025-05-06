from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from fastapi.exceptions import HTTPException

from core import session_local
from core.users import AuthenticatedUser
from util import get_user_from_token


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def get_user(
    authorization: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> AuthenticatedUser:
    if authorization.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")

    token = authorization.credentials
    return get_user_from_token(token)