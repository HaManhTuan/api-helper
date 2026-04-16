"""
Utility functions for testing.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.user import User
from app.repositories.concrete.user_repository import user_repository


async def create_test_user(
    db: AsyncSession,
    email: str = "test@example.com",
    phone: Optional[str] = None,
    password: str = "password123",
    role: str = "customer",
    status: str = "active",
    deleted_at: Optional[datetime] = None,
) -> User:
    """
    Create a test user in the database.
    """
    if phone is None:
        phone = "0900000000"

    # Check if user already exists using direct query to ensure tables exist
    try:
        result = await db.execute(select(User).filter(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            return existing_user
    except Exception as e:
        # If there's an error, log it and continue to create a new user
        print(f"Error checking for existing user: {str(e)}")
        # This likely means the table doesn't exist yet

    user = User(
        email=email,
        phone=phone,
        role=role,
        status=status,
        password=password,  # The model will hash it
    )
    # Set deleted_at if provided (for testing soft-deleted users)
    if deleted_at is not None:
        user.deleted_at = deleted_at

    db.add(user)
    await db.commit()

    return user


def create_test_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a test JWT token for a user.
    """
    identifier = f"testuser_{user_id}@example.com"
    to_encode = {"sub": identifier, "roles": ["customer"], "permissions": []}

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def create_test_token_for_user(user, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a test JWT token for a user object.
    """
    to_encode = {"sub": user.identifier, "roles": [user.role], "permissions": []}

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def get_auth_headers(token: str) -> Dict[str, str]:
    """
    Create authorization headers with the given token.
    """
    return {"Authorization": f"Bearer {token}"}
