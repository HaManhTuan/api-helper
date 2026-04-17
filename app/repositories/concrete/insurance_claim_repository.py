from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insurance_claim import InsuranceClaim
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class InsuranceClaimRepository(RepositoryImpl[InsuranceClaim]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(InsuranceClaim)
        super().__init__(
            model=InsuranceClaim,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_claims(self, db: AsyncSession, *, status: Optional[str], booking_id: Optional[str]) -> List[InsuranceClaim]:
        stmt = select(InsuranceClaim).where(InsuranceClaim.deleted_at.is_(None))
        if status:
            stmt = stmt.where(InsuranceClaim.status == status)
        if booking_id:
            stmt = stmt.where(InsuranceClaim.booking_id == booking_id)
        stmt = stmt.order_by(InsuranceClaim.created_at.desc())
        rows = await db.execute(stmt)
        return list(rows.scalars().all())


insurance_claim_repository = InsuranceClaimRepository()
