"""Data schemas for working with statistic calculating in FastAPI."""
from typing import Annotated

from pydantic import BaseModel, Field

class StatsBase(BaseModel):
    """Basic schema for all statistic research."""
    pass


class UserBalanceStats(StatsBase):
    """For issuing basic human statistics."""
    user_id: Annotated[int, Field(
        ...,
        description='The unique index of the REGISTERED user'
    )]
    user_name: Annotated[str, Field(
        ...,
        description='The name of the REGISTERED user with the specified index'
    )]
    total_amount: Annotated[float, Field(
        ...,
        description='Total account amount'
    )]
    account_count: Annotated[int, Field(
        ...,
        description='Number of accounts'
    )]
    avg_transaction_per_day: Annotated[float, Field(
        ...,
        description='Average transaction amount per day'
    )]
    avg_transaction_per_month: Annotated[float, Field(
        ...,
        description='Average transaction amount per month'
    )]


class UserCategorySpending(StatsBase):
    """Schema to issue a transaction by category."""
    category: Annotated[str, Field(
        ...,
        description='The category for which it is considered a waste'
    )]
    cat_amount: Annotated[float, Field(
        ...,
        description='The total amount for the specified category'
    )]
