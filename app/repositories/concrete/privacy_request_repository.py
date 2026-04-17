from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.privacy_request import PrivacyRequest
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class PrivacyRequestRepository(RepositoryImpl[PrivacyRequest]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(PrivacyRequest)
        super().__init__(
            model=PrivacyRequest,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_by_customer(self, db: AsyncSession, customer_id: str) -> List[PrivacyRequest]:
        result = await db.execute(
            select(PrivacyRequest)
            .where(PrivacyRequest.deleted_at.is_(None), PrivacyRequest.customer_id == customer_id)
            .order_by(PrivacyRequest.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id_and_customer(self, db: AsyncSession, request_id: str, customer_id: str) -> PrivacyRequest | None:
        result = await db.execute(
            select(PrivacyRequest).where(
                PrivacyRequest.deleted_at.is_(None),
                PrivacyRequest.id == request_id,
                PrivacyRequest.customer_id == customer_id,
            )
        )
        return result.scalar_one_or_none()


privacy_request_repository = PrivacyRequestRepository()
