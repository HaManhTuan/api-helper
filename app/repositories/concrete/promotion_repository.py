from datetime import datetime
from typing import Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promotion import Promotion
from app.models.promotion_redemption import PromotionRedemption
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class PromotionRepository(RepositoryImpl[Promotion]):
    def __init__(self) -> None:
        unified_repo = repository_factory.create_repository(Promotion)
        super().__init__(
            model=Promotion,
            query_builder=unified_repo.query_builder,
            optimistic_lock_validator=unified_repo.optimistic_lock_validator,
        )

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Promotion]:
        result = await db.execute(
            select(Promotion).where(
                Promotion.deleted_at.is_(None),
                func.lower(Promotion.code) == code.lower(),
            )
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def resolve_active(self, db: AsyncSession, *, code: str, at: datetime, service_id: Optional[str]) -> Optional[Promotion]:
        stmt = (
            select(Promotion)
            .where(
                and_(
                    Promotion.deleted_at.is_(None),
                    Promotion.active.is_(True),
                    func.lower(Promotion.code) == code.lower(),
                    Promotion.effective_from <= at,
                    or_(Promotion.effective_to.is_(None), Promotion.effective_to > at),
                    or_(Promotion.service_id.is_(None), Promotion.service_id == service_id),
                )
            )
            .order_by((Promotion.service_id == service_id).desc(), Promotion.effective_from.desc())
        )
        result = await db.execute(stmt.limit(1))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def count_redemptions(self, db: AsyncSession, *, promotion_id: str) -> int:
        result = await db.execute(
            select(func.count(PromotionRedemption.id)).where(
                PromotionRedemption.deleted_at.is_(None),
                PromotionRedemption.promotion_id == promotion_id,
                PromotionRedemption.status.in_(["reserved", "consumed"]),
            )
        )
        return int(result.scalar_one() or 0)

    async def count_redemptions_by_customer(self, db: AsyncSession, *, promotion_id: str, customer_id: str) -> int:
        result = await db.execute(
            select(func.count(PromotionRedemption.id)).where(
                PromotionRedemption.deleted_at.is_(None),
                PromotionRedemption.promotion_id == promotion_id,
                PromotionRedemption.customer_id == customer_id,
                PromotionRedemption.status.in_(["reserved", "consumed"]),
            )
        )
        return int(result.scalar_one() or 0)


promotion_repository = PromotionRepository()
