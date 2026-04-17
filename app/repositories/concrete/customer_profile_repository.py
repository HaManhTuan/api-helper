from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer_profile import CustomerProfile
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class CustomerProfileRepository(RepositoryImpl[CustomerProfile]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(CustomerProfile)
        super().__init__(
            model=CustomerProfile,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> CustomerProfile | None:
        row = await db.execute(
            select(CustomerProfile).where(CustomerProfile.deleted_at.is_(None), CustomerProfile.user_id == user_id)
        )
        return row.scalar_one_or_none()


customer_profile_repository = CustomerProfileRepository()
