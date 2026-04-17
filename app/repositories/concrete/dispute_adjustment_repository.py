from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dispute_adjustment import DisputeAdjustment
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class DisputeAdjustmentRepository(RepositoryImpl[DisputeAdjustment]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(DisputeAdjustment)
        super().__init__(
            model=DisputeAdjustment,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_by_dispute(self, db: AsyncSession, dispute_id: str) -> List[DisputeAdjustment]:
        result = await db.execute(
            select(DisputeAdjustment)
            .where(DisputeAdjustment.deleted_at.is_(None), DisputeAdjustment.dispute_id == dispute_id)
            .order_by(DisputeAdjustment.created_at.desc())
        )
        return list(result.scalars().all())


dispute_adjustment_repository = DisputeAdjustmentRepository()
