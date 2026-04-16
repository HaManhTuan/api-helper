from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service_offering import ServiceOffering
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class ServiceOfferingRepository(RepositoryImpl[ServiceOffering]):
    def __init__(self) -> None:
        unified_repo = repository_factory.create_repository(ServiceOffering)
        super().__init__(
            model=ServiceOffering,
            query_builder=unified_repo.query_builder,
            optimistic_lock_validator=unified_repo.optimistic_lock_validator,
        )

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[ServiceOffering]:
        result = await db.execute(select(ServiceOffering).where(ServiceOffering.code == code, ServiceOffering.deleted_at.is_(None)))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]


service_offering_repository = ServiceOfferingRepository()

