from datetime import datetime
from typing import Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tax_rule import TaxRule
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class TaxRuleRepository(RepositoryImpl[TaxRule]):
    def __init__(self) -> None:
        unified_repo = repository_factory.create_repository(TaxRule)
        super().__init__(
            model=TaxRule,
            query_builder=unified_repo.query_builder,
            optimistic_lock_validator=unified_repo.optimistic_lock_validator,
        )

    async def resolve_active(self, db: AsyncSession, *, service_offering_id: str, at: datetime) -> Optional[TaxRule]:
        base_filters = [
            TaxRule.deleted_at.is_(None),
            TaxRule.active.is_(True),
            TaxRule.effective_from <= at,
            or_(TaxRule.effective_to.is_(None), TaxRule.effective_to > at),
        ]

        stmt = (
            select(TaxRule)
            .where(
                and_(
                    *base_filters,
                    or_(TaxRule.service_offering_id == service_offering_id, TaxRule.service_offering_id.is_(None)),
                )
            )
            .order_by(
                (TaxRule.service_offering_id == service_offering_id).desc(),
                TaxRule.priority.desc(),
                TaxRule.effective_from.desc(),
            )
        )
        result = await db.execute(stmt.limit(1))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]


tax_rule_repository = TaxRuleRepository()

