from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insurance_enrollment import InsuranceEnrollment
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class InsuranceEnrollmentRepository(RepositoryImpl[InsuranceEnrollment]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(InsuranceEnrollment)
        super().__init__(
            model=InsuranceEnrollment,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_enrollments(
        self,
        db: AsyncSession,
        *,
        helper_id: Optional[str] = None,
        product_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[InsuranceEnrollment]:
        stmt = select(InsuranceEnrollment).where(InsuranceEnrollment.deleted_at.is_(None))
        if helper_id:
            stmt = stmt.where(InsuranceEnrollment.helper_id == helper_id)
        if product_id:
            stmt = stmt.where(InsuranceEnrollment.product_id == product_id)
        if status:
            stmt = stmt.where(InsuranceEnrollment.status == status)
        stmt = stmt.order_by(InsuranceEnrollment.updated_at.desc())
        rows = await db.execute(stmt)
        return list(rows.scalars().all())

    async def has_active_coverage(self, db: AsyncSession, *, helper_id: str, at: datetime) -> bool:
        stmt = (
            select(InsuranceEnrollment.id)
            .where(
                InsuranceEnrollment.deleted_at.is_(None),
                InsuranceEnrollment.helper_id == helper_id,
                InsuranceEnrollment.status == "active",
                InsuranceEnrollment.effective_from.is_not(None),
                InsuranceEnrollment.effective_to.is_not(None),
                and_(InsuranceEnrollment.effective_from <= at, InsuranceEnrollment.effective_to >= at),
            )
            .limit(1)
        )
        return (await db.execute(stmt)).scalar_one_or_none() is not None


insurance_enrollment_repository = InsuranceEnrollmentRepository()
