"""Data schemas for working with accounts in FastAPI."""
from typing import Annotated

from pydantic import BaseModel, Field

from .user import UserResponse

class AccountBase(BaseModel):
    """Basic schema for accounts."""
    account_name: Annotated[str, Field(
        default='Unnamed',
        description='Name of account',
        max_length=15
    )]
    amount: Annotated[float, Field(
        default=0.0,
        ge=0,
        description='Account amount'
    )]
    user_id: Annotated[int, Field(
        ...,
        description='The unique index of the REGISTERED account holder'
    )]


class AccountCreate(AccountBase):
    """Schema for creating new accounts."""
    pass


class AccountResponse(AccountBase):
    """Account schema for work with database."""
    id: Annotated[int, Field(
        ...,
        description='Automatic unique indexing'
    )]
    user: Annotated[UserResponse, Field(
        ...,
        description='The existing Account Holder found by id'
    )]

    class Config:
        """Pydantic configuration."""
        from_attributes = True
