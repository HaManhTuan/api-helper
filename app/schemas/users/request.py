"""
User request and response schemas.

This module contains schemas for API requests and responses
for user-related operations.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import EmailStr, Field, field_validator, model_validator

from app.schemas.common.base_schema import BaseSchema

# ===== REQUEST SCHEMAS (Data In) =====


class UserRegistrationRequest(BaseSchema):
    """Schema for user registration request from API"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=8, max_length=20)
    password: str = Field(..., min_length=8)
    role: str = Field(default="customer", min_length=3, max_length=20)

    @model_validator(mode="after")
    def validate_identifier(self) -> "UserRegistrationRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        return self


class UserLoginRequest(BaseSchema):
    """Schema for login request using identifier/password."""

    identifier: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8)


class UserCreateRequest(BaseSchema):
    """Schema for user creation request from API"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=8, max_length=20)
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    role: str = Field(default="customer", min_length=3, max_length=20)
    status: str = Field(default="active", min_length=3, max_length=20)

    @field_validator("password_confirm")  # type: ignore[misc]
    @classmethod
    def passwords_match(cls, v: str, info: Any) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

    @model_validator(mode="after")
    def validate_identifier(self) -> "UserCreateRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        return self


class UserUpdateRequest(BaseSchema):
    """Schema for user update request from API"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    role: Optional[str] = Field(None, min_length=3, max_length=20)
    status: Optional[str] = Field(None, min_length=3, max_length=20)
    updated_at: Optional[str] = Field(None, description="Required for optimistic locking")


# ===== RESPONSE SCHEMAS (Data Out) =====


class UserResponse(BaseSchema):
    """Schema for user response to API clients"""

    id: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class UserProfileResponse(BaseSchema):
    """Schema for user profile response (includes sensitive fields)"""

    id: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
