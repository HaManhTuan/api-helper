"""
User schema conversion utilities.

This module provides functions to convert between user request schemas (API input)
and internal schemas (application logic).
"""

from app.schemas.users.request import UserCreateRequest, UserRegistrationRequest, UserUpdateRequest
from app.schemas.users.schema import UserCreate, UserUpdate


def convert_user_registration_to_internal(request: UserRegistrationRequest) -> UserCreate:
    """Convert user registration request to internal user creation schema"""
    return UserCreate(
        email=request.email,
        phone=request.phone,
        password=request.password,
        role=request.role,
        status="active",
    )


def convert_user_create_request_to_internal(request: UserCreateRequest) -> UserCreate:
    """Convert user creation request to internal user creation schema"""
    return UserCreate(
        email=request.email,
        phone=request.phone,
        password=request.password,
        role=request.role,
        status=request.status,
    )


def convert_user_update_request_to_internal(request: UserUpdateRequest) -> UserUpdate:
    """Convert user update request to internal user update schema"""
    return UserUpdate(
        email=request.email,
        phone=request.phone,
        role=request.role,
        status=request.status,
        updated_at=request.updated_at,
    )
