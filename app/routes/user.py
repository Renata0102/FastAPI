"""Processing requests from /users/."""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
)
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED

from ..database.dependencies import get_db
from ..database.models import User
from ..schemas.user import UserCreate, UserResponse
from ..utils.authorisation_password import (
    get_current_user_with_login_and_password,
    get_password_hash,
)
from ..utils.authorisation_token import (
    encode_jwt,
    get_current_user_with_token,
    http_bearer,
)
from ..utils.users_rights import (
    check_admin_rights,
    http_wrong_rights,
    is_admin_id, check_user_exists,
)


router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBasic()


@router.post(
    '/register',
    response_model=UserResponse,
    status_code=HTTP_201_CREATED,
    summary='Register new user'
)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Register a new user in the system."""
    existing_user = db.query(User).filter(User.login == user.login).first()
    if existing_user:
        raise HTTPException(
            status_code=422,
            detail=f"User with username {user.login} already exists"
        )

    db_user = User(
        login=user.login,
        is_admin=False,
        password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get(
    '/authorise-with-password',
    summary="Authorize with login and password"
)
async def login_with_password(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> UserResponse:
    """Get authenticated user's information."""
    db_user = get_current_user_with_login_and_password(db, credentials.username,
                                                       credentials.password)
    return db_user


@router.get(
    '/authorise-with-token',
    summary='Authorize with token'
)
async def login_with_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> UserResponse:
    """Get user information using authorization token."""
    token = credentials.credentials
    db_user = get_current_user_with_token(token, db)
    if db_user:
        return db_user

    raise HTTPException(
        status_code=401,
        detail="Invalid token"
    )


@router.get(
    '/get-token',
    summary='Get user ID and access token'
)
async def get_access_token(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> dict:
    """Get access token and user ID for authenticated users."""
    db_user = get_current_user_with_login_and_password(db, credentials.username,
                                                       credentials.password)

    return {
        "user_id": db_user.id,
        "access_token": encode_jwt({'sub': db_user.login}),
        "token_type": "bearer"
    }


@router.get(
    '/get-all',
    response_model=List[UserResponse],
    summary='Get all users (admin only)'
)
async def get_users(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> List[UserResponse]:
    """ADMIN ONLY - Retrieve list of all users."""
    if check_admin_rights(
            db,
            credentials.username,
            credentials.password
    ):
        return db.query(User).all()

    raise http_wrong_rights


@router.delete(
    '/{user_id}',
    summary='Delete user by ID'
)
async def delete_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_id: int = Path(..., description="User ID to delete", ge=0),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Delete user by ID. Admin only or self-deletion.

    user_id == 0 for self-deletion.
    """
    db_user = get_current_user_with_login_and_password(db, credentials.username,
                                                       credentials.password)

    if user_id == 0:
        user_id = db_user.id
        user_to_delete = check_user_exists(user_id, db)
        is_admin_id(user_id, db)
        correct_id = True
    else:
        user_to_delete = check_user_exists(user_id, db)
        is_admin_id(user_id, db)
        correct_id = user_id == db_user.id

    if correct_id or db_user.is_admin:
        db.delete(user_to_delete)
        db.commit()
        return user_to_delete
    raise http_wrong_rights


@router.put(
    '/{user_id}',
    summary='Update user by ID'
)
async def change_user(
    user: UserCreate,
    user_id: int = Path(..., description="User ID to update", ge=0),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> UserResponse:
    """
    Update user credentials by ID.
    Admin only or self-update.

    user_id == 0 for self-update.
    """
    current_user = get_current_user_with_token(credentials.credentials, db)
    is_admin = current_user.is_admin

    if user_id == 0:
        user_id = current_user.id
        db_user = current_user
        correct_id = True
    else:
        db_user = db.query(User).filter(User.id == user_id).first()
        correct_id = user_id == current_user.id

    is_admin_id(user_id, db)

    if correct_id or is_admin:
        db_user.login = user.login
        db_user.password = get_password_hash(user.password)
        db.commit()
        db.refresh(db_user)
        return db_user
    raise http_wrong_rights
