from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class UserRepository(RepositoryImpl[User]):
    """Repository for User model extending from unified repository"""

    def __init__(self) -> None:
        # Create unified repository using factory and inherit its components
        unified_repo = repository_factory.create_repository(User)
        # Initialize the base class with the same components
        super().__init__(
            model=User,
            query_builder=unified_repo.query_builder,
            optimistic_lock_validator=unified_repo.optimistic_lock_validator,
        )

    # User-specific methods that can't be handled by base repository
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_by_phone(self, db: AsyncSession, phone: str) -> Optional[User]:
        """Get user by phone"""
        result = await db.execute(select(User).filter(User.phone == phone))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_by_identifier(self, db: AsyncSession, identifier: str) -> Optional[User]:
        """Get user by login identifier (email or phone)."""
        result = await db.execute(select(User).filter(or_(User.email == identifier, User.phone == identifier)))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Backward-compatible alias for identifier lookup."""
        return await self.get_by_identifier(db=db, identifier=username)


# Create instance for dependency injection
user_repository = UserRepository()
