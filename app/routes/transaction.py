"""Processing requests from /transactions/."""
from datetime import date
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED

from ..database.dependencies import get_db
from ..database.models import Transaction
from ..schemas.transaction import TransactionCreate, TransactionResponse
from ..utils.users_rights import (
    check_account_exists,
    check_admin_rights,
    check_transaction_exists,
    check_user_exists,
    check_user_rights,
    http_wrong_rights,
    is_admin_id,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])
security = HTTPBasic()


@router.post(
    '/',
    response_model=TransactionResponse,
    status_code=HTTP_201_CREATED
)
async def create_transaction(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    trans: TransactionCreate,
    db: Session = Depends(get_db)
) -> TransactionResponse:
    """Create a new transaction linked to a user and account."""
    db_user = check_user_exists(trans.user_id, db)
    is_admin_id(trans.user_id, db)

    check_user_rights(
        db,
        db_user,
        credentials.username,
        credentials.password
    )
    db_account = check_account_exists(trans.account_id, db)

    if db_account.user_id != db_user.id:
        raise HTTPException(
            status_code=409,
            detail='The user does not have such an account'
        )

    allowed_categories = {
        True: ['Salary', 'Bonus', 'Scholarship', 'Gift', 'Other income'],
        False: ['Products', 'Clothing', 'Subscriptions', 'Other expenses']
    }
    if trans.category not in allowed_categories[trans.amount >= 0]:
        raise HTTPException(
            status_code=404,
            detail=f"Category not found. For {'positive' if trans.amount > 0 else 'negative'} "
                  f"amount it can be: {', '.join(allowed_categories[trans.amount > 0])}"
        )

    new_account_amount = db_account.amount + trans.amount
    if new_account_amount < 0:
        raise HTTPException(
            status_code=406,
            detail='The amount of the expense exceeds the balance amount'
        )
    db_account.amount = new_account_amount

    db_transaction = Transaction(
        category=trans.category,
        amount=trans.amount,
        date=date.today(),
        user=db_user,
        user_id=db_user.id,
        account=db_account,
        account_id=db_account.id
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    db.refresh(db_account)
    return db_transaction


@router.get('/', response_model=List[TransactionResponse])
async def get_transactions(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> List[TransactionResponse]:
    """Only for admin. Retrieve a list of all transactions."""
    if check_admin_rights(
        credentials.username,
        credentials.password
    ):
        return db.query(Transaction).all()

    raise http_wrong_rights


@router.get('/{user_id}', response_model=List[TransactionResponse],
            summary='Get all accounts by ID')
async def get_transactions_by_id(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_id: int = Path(..., description="User ID to get transactions", ge=1),
    db: Session = Depends(get_db)
) -> List[TransactionResponse]:
    """Only for admin or for getting own transactions."""
    db_user = check_user_exists(user_id, db)

    check_user_rights(
        db,
        db_user,
        credentials.username,
        credentials.password
    )

    return db.query(Transaction).filter(Transaction.user_id == user_id).all()


@router.delete('/{trans_id}', response_model=TransactionResponse)
async def delete_transaction(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    trans_id: int = Path(..., description="Transaction ID to delete", ge=1),
    db: Session = Depends(get_db)
) -> TransactionResponse:
    """Delete a transaction by ID and adjust the corresponding account balance."""
    db_transaction = check_transaction_exists(trans_id, db)
    db_user = check_user_exists(db_transaction.user_id, db)

    check_user_rights(
        db,
        db_user,
        credentials.username,
        credentials.password
    )
    db_account = check_account_exists(db_transaction.account_id, db)
    new_account_amount = db_account.amount - db_transaction.amount
    if new_account_amount < 0:
        raise HTTPException(
            status_code=406,
            detail='The new amount of the expense exceeds the balance amount. '
                   'The balance cannot be negative'
        )
    db_account.amount = new_account_amount

    db.delete(db_transaction)
    db.commit()
    db.refresh(db_account)
    return db_transaction


@router.put('/{trans_id}', response_model=TransactionResponse)
async def change_transaction(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    trans: TransactionCreate,
    trans_id: int = Path(..., description="Transaction ID to change", ge=1),
    db: Session = Depends(get_db)
) -> TransactionResponse:
    """Update an existing transaction by ID and adjust the corresponding."""
    db_transaction = check_transaction_exists(trans_id, db)
    db_user = check_user_exists(trans.user_id, db)

    check_user_rights(
        db,
        db_user,
        credentials.username,
        credentials.password
    )

    db_account = check_account_exists(trans.account_id, db)

    if db_account.user_id != db_user.id:
        raise HTTPException(
            status_code=409,
            detail='The user does not have such an account'
        )
    allowed_categories = {
        True: ['Salary', 'Bonus', 'Scholarship', 'Gift', 'Other income'],
        False: ['Products', 'Clothing', 'Subscriptions', 'Other expenses']
    }
    if trans.category not in allowed_categories[trans.amount > 0]:
        raise HTTPException(
            status_code=404,
            detail=f"Category not found. For {'positive' if trans.amount > 0 else 'negative'} "
                  f"amount it can be: {', '.join(allowed_categories[trans.amount > 0])}"
        )

    new_account_amount = (db_account.amount - db_transaction.amount + trans.amount)
    if new_account_amount < 0:
        raise HTTPException(
            status_code=406,
            detail='The new amount of the expense exceeds the balance amount. '
                   'The balance cannot be negative'
        )
    db_account.amount = new_account_amount

    db_transaction.category = trans.category
    db_transaction.amount = trans.amount
    db_transaction.user_id = trans.user_id
    db_transaction.account_id = trans.account_id

    db.commit()
    db.refresh(db_transaction)
    db.refresh(db_account)
    return db_transaction
