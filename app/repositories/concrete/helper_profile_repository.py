from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.helper_profile import HelperProfile
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class HelperProfileRepository(RepositoryImpl[HelperProfile]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(HelperProfile)
        super().__init__(
            model=HelperProfile,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> Optional[HelperProfile]:
        result = await db.execute(
            select(HelperProfile).where(HelperProfile.user_id == user_id, HelperProfile.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def list_by_status(self, db: AsyncSession, approval_status: Optional[str]) -> List[HelperProfile]:
        stmt = select(HelperProfile).where(HelperProfile.deleted_at.is_(None))
        if approval_status:
            stmt = stmt.where(HelperProfile.approval_status == approval_status)
        stmt = stmt.order_by(HelperProfile.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())


helper_profile_repository = HelperProfileRepository()
