'''File with methods for authorisation users with login and password'''

from passlib.context import CryptContext
from fastapi import HTTPException
from fastapi.security import HTTPBasic, HTTPBearer

from ..database.models import User
from ..schemas.user import UserResponse

http_wrong_credentials = HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
security = HTTPBasic()
http_bearer = HTTPBearer()


def get_password_hash(password: str) -> str:
    '''
    Password hashing function
    '''
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    '''
    Password verification function
    '''
    return pwd_context.verify(password, hashed_password)


def get_current_user_with_login_and_password(
        db,
        login: str,
        password: str
) -> UserResponse:
    print('I am here')
    '''
    Verifies the user's existence
    If the password is specified, it checks the password
    Return user
    '''
    db_user = db.query(User).filter(User.login == login).first()
    if db_user:
        if verify_password(password, db_user.password):
            return db_user
    raise http_wrong_credentials



