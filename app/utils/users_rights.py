'''Verification functions during user authorization'''
from fastapi import HTTPException

from .authorisation_password import get_current_user_with_login_and_password
from ..database.models import Account, Transaction, User
from ..schemas.account import AccountResponse
from ..schemas.transaction import TransactionResponse
from ..schemas.user import UserResponse
from ..utils.authorisation_password import verify_password
from ..utils.config import settings

http_wrong_rights = HTTPException(
        status_code=403,
        detail="No access rights"
    )

def check_admin_rights(db, login: str, password: str) -> bool:
    '''Check is user admin'''
    db_user = get_current_user_with_login_and_password(db, login, password)
    return db_user.is_admin

def is_admin_id(user_id, db):
    '''Check is it user's id'''
    if (db
        .query(User)
        .filter(User.id == user_id)
        .first()
        .login) == settings.DB_USER:
        raise http_wrong_rights

def check_user_exists(id, db) -> UserResponse:
    '''Find user by id'''
    if db_user := db.query(User).filter(User.id == id).first():
        return db_user
    raise HTTPException(
        status_code=404,
        detail='User not found'
    )

def check_account_exists(id, db) -> AccountResponse:
    '''Find account by id'''
    if db_account := db.query(Account).filter(Account.id == id).first():
        return db_account
    raise HTTPException(
        status_code=404,
        detail='Account not found'
    )

def check_transaction_exists(id, db) -> TransactionResponse:
    '''Find transaction by id'''
    if db_transaction := (db.query(Transaction)
            .filter(Transaction.id == id).first()):
        return db_transaction
    raise HTTPException(
        status_code=404,
        detail='Transaction not found'
    )

def check_user_rights(db, db_user: User, cred_log, cred_pass):
    '''Check rights for editing'''
    is_admin = check_admin_rights(db, cred_log, cred_pass)

    has_rights = (db_user.login == cred_log
                  and verify_password(cred_pass, db_user.password))

    if not (is_admin or has_rights):
        raise http_wrong_rights
