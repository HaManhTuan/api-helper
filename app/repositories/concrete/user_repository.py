from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
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

    async def list_internal_staff(self, db: AsyncSession) -> List[User]:
        """List all internal staff/admin accounts."""
        result = await db.execute(select(User).filter(User.role.in_(["staff", "admin"])))
        return list(result.scalars().all())

    async def get_permission_codes(self, db: AsyncSession, user_id: str) -> List[str]:
        """
        Resolve effective permission codes for a user from role mapping.
        """
        from app.models.permission import Permission
        from app.models.role_permission import RolePermission
        from app.models.user import User

        stmt = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(User, User.staff_role_id == RolePermission.role_id)
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        result = await db.execute(stmt)
        return [code for code in result.scalars().all()]

    async def list_customers_paginated(
        self,
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        base_filters = [User.deleted_at.is_(None), User.role == "customer"]
        if status:
            base_filters.append(User.status == status)
        if search:
            keyword = f"%{search.strip()}%"
            base_filters.append(
                or_(
                    User.email.ilike(keyword),
                    User.phone.ilike(keyword),
                    User.identifier.ilike(keyword),
                )
            )

        count_stmt = select(func.count()).select_from(User).where(*base_filters)
        total = int((await db.execute(count_stmt)).scalar_one() or 0)

        stmt = (
            select(User)
            .where(*base_filters)
            .order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    async def count_customer_bookings(self, db: AsyncSession, *, customer_id: str) -> dict:
        from app.models.booking import Booking

        rows = await db.execute(
            select(Booking.status, func.count())
            .where(Booking.deleted_at.is_(None), Booking.customer_id == customer_id)
            .group_by(Booking.status)
        )
        counters = {status: int(total) for status, total in rows.all()}
        counters["total"] = sum(counters.values())
        return counters

    async def set_customer_status(
        self,
        db: AsyncSession,
        *,
        customer_id: str,
        new_status: str,
        expected_updated_at: Optional[datetime] = None,
    ) -> User:
        payload = {"status": new_status}
        return await self.update_with_optimistic_lock(
            db=db,
            id=customer_id,
            obj_in=payload,
            expected_updated_at=expected_updated_at.isoformat() if expected_updated_at else None,
        )


# Create instance for dependency injection
user_repository = UserRepository()
