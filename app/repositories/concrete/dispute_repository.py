from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dispute import Dispute
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class DisputeRepository(RepositoryImpl[Dispute]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(Dispute)
        super().__init__(
            model=Dispute,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_cases(
        self,
        db: AsyncSession,
        *,
        status: Optional[str],
        booking_id: Optional[str],
        owner_staff_id: Optional[str],
    ) -> List[Dispute]:
        stmt = select(Dispute).where(Dispute.deleted_at.is_(None))
        if status:
            stmt = stmt.where(Dispute.status == status)
        if booking_id:
            stmt = stmt.where(Dispute.booking_id == booking_id)
        if owner_staff_id:
            stmt = stmt.where(Dispute.owner_staff_id == owner_staff_id)
        stmt = stmt.order_by(Dispute.opened_at.desc(), Dispute.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())


dispute_repository = DisputeRepository()
