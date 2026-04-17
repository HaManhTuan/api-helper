from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payout_batch import PayoutBatch
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class PayoutBatchRepository(RepositoryImpl[PayoutBatch]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(PayoutBatch)
        super().__init__(
            model=PayoutBatch,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_batches(self, db: AsyncSession, *, status: Optional[str] = None) -> List[PayoutBatch]:
        stmt = select(PayoutBatch).where(PayoutBatch.deleted_at.is_(None)).order_by(PayoutBatch.created_at.desc())
        if status:
            stmt = stmt.where(PayoutBatch.status == status)
        rows = await db.execute(stmt)
        return list(rows.scalars().all())


payout_batch_repository = PayoutBatchRepository()
