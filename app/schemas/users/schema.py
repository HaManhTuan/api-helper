"""
User internal schemas.

This module contains schemas used internally within the application
for user-related operations.
"""

from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field, model_validator

from app.schemas.common.base_schema import BaseSchema


class UserBase(BaseSchema):
    """Base schema for user data used internally"""

    role: str = Field(default="customer", min_length=3, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=8, max_length=20)
    status: str = Field(default="active", min_length=3, max_length=20)


class UserCreate(UserBase):
    """Schema for user creation used internally in the application"""

    password: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def validate_identifier(self) -> "UserCreate":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        return self


class UserUpdate(BaseSchema):
    """Schema for user update used internally in the application"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    role: Optional[str] = Field(None, min_length=3, max_length=20)
    status: Optional[str] = Field(None, min_length=3, max_length=20)
    updated_at: Optional[str] = Field(None, description="Required for optimistic locking")


class UserInDB(UserBase):
    """Schema for user data in database"""

    id: str
    password_hash: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
