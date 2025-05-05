'''File with methods for authorisation users with token'''

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
from passlib.context import CryptContext

from ..database.models import User
from ..schemas.user import UserResponse
from ..utils.config import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
http_bearer = HTTPBearer()


def encode_jwt(data: dict,
               time_action: timedelta | None = None) -> str:
    '''
    Create token with username
    '''

    to_encode = data.copy()

    if not time_action:
        expire = (datetime.now(timezone.utc)
                  + timedelta(days=settings.ACCESS_DAYS))
    else:
        expire = (datetime.now(timezone.utc)
                  + time_action)

    to_encode.update({"exp": expire})

    encoded = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded


def decode_jwt(token: str) -> dict:
    '''
    Decoding of the token with expiration verification
    '''
    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=settings.ALGORITHM
    )
    if datetime.fromtimestamp(decoded['exp']) < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail='Inactive user'
        )
    else:
        return decoded


def get_current_user_with_token(token: Annotated[str, Depends(http_bearer)],
                     db) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token)
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    db_user = db.query(User).filter(User.login == login).first()

    if db_user is None:
        raise credentials_exception
    return db_user
