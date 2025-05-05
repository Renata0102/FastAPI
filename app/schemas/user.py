"""Data schemas for working with user in FastAPI."""

from typing import Annotated

from pydantic import BaseModel, Field

class UserBase(BaseModel):
    """Basic schema for users."""
    login: Annotated[str, Field(
        default='Unnamed',
        description='Login of a user'
    )]
    password: Annotated[str, Field(
        ...,
        description='Password of a user',
        min_length=3
    )]


class UserCreate(UserBase):
    """Schema for creating new users."""
    pass


class UserResponse(UserBase):
    """User schema for work with database."""
    id: Annotated[int, Field(
        ...,
        description='Automatic unique indexing'
    )]
    is_admin: Annotated[bool, Field(
        default=False,
        description='Access rights'
    )]

    class Config:
        """Pydantic configuration."""
        from_attributes = True
