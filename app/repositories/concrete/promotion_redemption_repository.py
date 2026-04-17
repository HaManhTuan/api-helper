from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promotion_redemption import PromotionRedemption
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class PromotionRedemptionRepository(RepositoryImpl[PromotionRedemption]):
    def __init__(self) -> None:
        unified_repo = repository_factory.create_repository(PromotionRedemption)
        super().__init__(
            model=PromotionRedemption,
            query_builder=unified_repo.query_builder,
            optimistic_lock_validator=unified_repo.optimistic_lock_validator,
        )

    async def has_consumed_for_booking(self, db: AsyncSession, *, booking_id: str) -> bool:
        result = await db.execute(
            select(PromotionRedemption.id).where(
                PromotionRedemption.deleted_at.is_(None),
                PromotionRedemption.booking_id == booking_id,
                PromotionRedemption.status == "consumed",
            )
        )
        return result.scalar_one_or_none() is not None

    async def latest_for_promotion(self, db: AsyncSession, *, promotion_id: str, limit: int = 100) -> list[PromotionRedemption]:
        result = await db.execute(
            select(PromotionRedemption)
            .where(
                PromotionRedemption.deleted_at.is_(None),
                PromotionRedemption.promotion_id == promotion_id,
            )
            .order_by(desc(PromotionRedemption.redeemed_at))
            .limit(limit)
        )
        return list(result.scalars().all())


promotion_redemption_repository = PromotionRedemptionRepository()
