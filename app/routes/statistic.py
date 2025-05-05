"""Processing requests from /stats/."""
from datetime import date
from typing import Annotated, List

from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database.dependencies import get_db
from ..database.models import Account, Transaction
from ..schemas.statistic import UserBalanceStats, UserCategorySpending
from ..utils.users_rights import check_user_exists, check_user_rights

router = APIRouter(prefix="/stats", tags=["statistics"])
security = HTTPBasic()


@router.get('/user-balances/{user_id}', response_model=UserBalanceStats)
async def get_balance_statistics(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_id: int = Path(..., description="User ID to calculate statistics", ge=1),
    db: Session = Depends(get_db)
) -> UserBalanceStats:
    """Retrieve aggregated balance statistics for a user."""
    db_user = check_user_exists(user_id, db)

    check_user_rights(
        db,
        db_user,
        credentials.username,
        credentials.password
    )

    # Get total amount and account count
    account_stats = db.query(
        func.sum(Account.amount).label('total_amount'),
        func.count(Account.id).label('account_count')
    ).filter(
        Account.user_id == user_id
    ).first()

    # Get transaction statistics
    transaction_stats = db.query(
        func.sum(Transaction.amount).label('total_transactions'),
        func.count(Transaction.id).label('transaction_count'),
        func.min(Transaction.date).label('first_date'),
        func.max(Transaction.date).label('last_date')
    ).filter(
        Transaction.user_id == user_id
    ).first()

    avg_per_day = 0.0
    avg_per_month = 0.0

    if transaction_stats and transaction_stats.transaction_count:
        total_days = (transaction_stats.last_date -
                     transaction_stats.first_date).days + 1
        total_months = total_days / 30.44  # Average days in month

        if total_days > 0:
            avg_per_day = transaction_stats.total_transactions / total_days
            avg_per_month = transaction_stats.total_transactions / total_months

    return UserBalanceStats(
        user_id=user_id,
        user_name=db_user.login,
        total_amount=account_stats.total_amount or 0.0 if account_stats else 0.0,
        account_count=account_stats.account_count or 0 if account_stats else 0,
        avg_transaction_per_day=avg_per_day,
        avg_transaction_per_month=avg_per_month
    )


@router.get('/monthly-category-spent/{user_id}',
           response_model=List[UserCategorySpending])
async def get_monthly_category_spent(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_id: int = Path(..., description="User ID to receive transactions", ge=1),
    month_trans: int = None,
    year_trans: int = None,
    db: Session = Depends(get_db)
) -> List[UserCategorySpending]:
    """Retrieve the monthly spending per category for a specific user."""
    db_user = check_user_exists(user_id, db)

    check_user_rights(
        db,
        db_user,
        credentials.username,
        credentials.password
    )

    current_year = year_trans if year_trans else date.today().year
    current_month = month_trans if month_trans else date.today().month

    first_day_of_month = date(current_year, current_month, 1)

    category_spending = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('cat_amount')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.date >= first_day_of_month,
        Transaction.date <= date.today()
    ).group_by(
        Transaction.category
    ).order_by(
        func.sum(Transaction.amount)
    ).all()

    return [
        UserCategorySpending(
            category=cat,
            cat_amount=cat_sp
        )
        for cat, cat_sp in category_spending
    ]
