"""Processing requests from /accounts/."""
from typing import Annotated, List

from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED

from ..database.dependencies import get_db
from ..database.models import Account
from ..schemas.account import AccountCreate, AccountResponse
from ..utils.authorisation_password import (
    get_current_user_with_login_and_password,
    security,
)
from ..utils.users_rights import (
    check_account_exists,
    check_admin_rights,
    check_user_exists,
    check_user_rights,
    http_wrong_rights,
    is_admin_id,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post('/',
             response_model=AccountResponse,
             status_code=HTTP_201_CREATED,
             summary='Create a new account for a registered user')
async def create_accounts(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    account: AccountCreate,
    db: Session = Depends(get_db)
) -> AccountResponse:
    """Create a new account for a registered user."""
    db_user = check_user_exists(account.user_id, db)
    is_admin_id(account.user_id, db)

    check_user_rights(
        db,
        db_user,
        credentials.username,
        credentials.password
    )

    db_account = Account(
        account_name=account.account_name,
        amount=account.amount,
        user=db_user,
        user_id=db_user.id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get('/get-all',
            response_model=List[AccountResponse],
            summary='Get all accounts (admin only)')
async def get_accounts(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> List[AccountResponse]:
    """Only for admin. Retrieve a list of all accounts."""
    if check_admin_rights(
        credentials.username,
        credentials.password
    ):
        return db.query(Account).all()

    raise http_wrong_rights


@router.get('/{user_id}',
            response_model=List[AccountResponse],
            summary='Get all accounts by user_id (user_id = 0 for own)')
async def get_accounts_by_id(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_id: int = Path(
        ...,
        description="User ID to get accounts", ge=0
    ),
    db: Session = Depends(get_db)
) -> List[AccountResponse]:
    """
    Only for admin.
    Retrieve a list of user's accounts.

    user_id == 0 for own accounts.
    """
    current_user = get_current_user_with_login_and_password(db,
                                                            credentials.username,
                                                            credentials.password)
    if user_id == 0:
        user_id = current_user.id
    else:
        db_user = check_user_exists(user_id, db)
        check_user_rights(
            db,
            db_user,
            credentials.username,
            credentials.password
        )

    return db.query(Account).filter(Account.user_id == user_id).all()


@router.delete('/{account_id}', response_model=AccountResponse)
async def delete_account(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    account_id: int = Path(..., description="Account ID to delete", ge=1),
    db: Session = Depends(get_db)
) -> AccountResponse:
    """Delete an account by its ID."""
    db_account = check_account_exists(account_id, db)
    db_user = check_user_exists(db_account.user_id, db)

    check_user_rights(
        db,
        db_user,
        credentials.username,
        credentials.password
    )

    db.delete(db_account)
    db.commit()
    return db_account


@router.put('/{account_id}', response_model=AccountResponse)
async def change_account(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    account: AccountCreate,
    account_id: int = Path(..., description="Account ID to change", ge=1),
    db: Session = Depends(get_db)
) -> AccountResponse:
    """Update an existing account's details by ID."""
    db_account = check_account_exists(account_id, db)
    db_user = check_user_exists(db_account.user_id, db)

    check_user_rights(
        db,
        db_user,
        credentials.username,
        credentials.password
    )
    db_account.account_name = account.account_name
    db_account.amount = account.amount
    db_account.user_id = account.user_id
    db.commit()
    db.refresh(db_account)
    return db_account
