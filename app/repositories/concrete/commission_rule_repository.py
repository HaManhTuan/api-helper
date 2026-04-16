from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commission_rule import CommissionRule
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class CommissionRuleRepository(RepositoryImpl[CommissionRule]):
    def __init__(self) -> None:
        unified_repo = repository_factory.create_repository(CommissionRule)
        super().__init__(
            model=CommissionRule,
            query_builder=unified_repo.query_builder,
            optimistic_lock_validator=unified_repo.optimistic_lock_validator,
        )

    async def list_for_service(self, db: AsyncSession, service_offering_id: Optional[str]) -> List[CommissionRule]:
        stmt = select(CommissionRule).where(CommissionRule.deleted_at.is_(None))
        if service_offering_id is None:
            stmt = stmt.where(CommissionRule.service_offering_id.is_(None))
        else:
            stmt = stmt.where(CommissionRule.service_offering_id == service_offering_id)
        stmt = stmt.order_by(CommissionRule.priority.desc(), CommissionRule.effective_from.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def resolve_active(
        self, db: AsyncSession, *, service_offering_id: str, at: datetime
    ) -> Optional[CommissionRule]:
        base_filters = [
            CommissionRule.deleted_at.is_(None),
            CommissionRule.active.is_(True),
            CommissionRule.effective_from <= at,
            or_(CommissionRule.effective_to.is_(None), CommissionRule.effective_to > at),
        ]

        # Deterministic precedence: service-specific overrides default (NULL).
        stmt = (
            select(CommissionRule)
            .where(
                and_(
                    *base_filters,
                    or_(CommissionRule.service_offering_id == service_offering_id, CommissionRule.service_offering_id.is_(None)),
                )
            )
            .order_by(
                (CommissionRule.service_offering_id == service_offering_id).desc(),
                CommissionRule.priority.desc(),
                CommissionRule.effective_from.desc(),
            )
        )
        result = await db.execute(stmt.limit(1))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]


commission_rule_repository = CommissionRuleRepository()

