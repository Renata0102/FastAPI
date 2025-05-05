"""Data schemas for working with transactions in FastAPI."""
from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, validator

from .account import AccountResponse
from .user import UserResponse

class TransactionBase(BaseModel):
    """Basic schema for transactions."""
    amount: Annotated[float, Field(
        default=0.0,
        description='Transaction amount'
    )]
    category: Annotated[str, Field(
        default='auto',
        description="Transaction category. "
        "For positive amounts: 'Salary', 'Bonus', 'Scholarship', "
        "'Gift', 'Other income', "
        "for negative amounts: 'Products', 'Clothing', "
        "'Subscriptions', 'Other expenses'."
        "If it is 'auto', then 'Other income' or 'Other expenses' "
        "is automatically indicated, depending on the amount sign."
    )]
    user_id: Annotated[int, Field(
        default=1,
        description='The unique index of the REGISTERED transaction maker'
    )]
    account_id: Annotated[int, Field(
        default=1,
        description='The unique index of the REGISTERED account'
    )]
    date: Annotated[date, Field(
        default_factory=date.today,
        description='Date of transaction'
    )]

    @validator('category', pre=True, always=True)
    def set_default_category(cls, v, values):
        """Set default category based on amount if category is 'auto'."""
        if v != 'auto':
            return v

        amount = values.get('amount', 0)
        return 'Other income' if amount >= 0 else 'Other expenses'


class TransactionCreate(TransactionBase):
    """Schema for creating new transactions."""
    pass


class TransactionResponse(TransactionBase):
    """Transaction schema for work with database."""
    id: Annotated[int, Field(
        ...,
        description='Automatic unique indexing'
    )]
    user: UserResponse
    account: AccountResponse

    class Config:
        """Pydantic configuration."""
        from_attributes = True
