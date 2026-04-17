from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class ReviewRepository(RepositoryImpl[Review]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(Review)
        super().__init__(
            model=Review,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_for_moderation(
        self,
        db: AsyncSession,
        *,
        booking_id: Optional[str] = None,
        helper_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        status: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Review]:
        stmt = select(Review).where(Review.deleted_at.is_(None))
        if booking_id:
            stmt = stmt.where(Review.booking_id == booking_id)
        if helper_id:
            stmt = stmt.where(Review.helper_id == helper_id)
        if customer_id:
            stmt = stmt.where(Review.customer_id == customer_id)
        if status:
            stmt = stmt.where(Review.status == status)
        if min_rating is not None:
            stmt = stmt.where(Review.rating >= min_rating)
        if max_rating is not None:
            stmt = stmt.where(Review.rating <= max_rating)
        if created_from:
            stmt = stmt.where(Review.created_at >= created_from)
        if created_to:
            stmt = stmt.where(Review.created_at <= created_to)

        stmt = stmt.order_by(Review.created_at.desc()).offset(skip).limit(limit)
        rows = await db.execute(stmt)
        return list(rows.scalars().all())

    async def aggregate_visible_for_helper(self, db: AsyncSession, helper_id: str) -> tuple[float, int]:
        stmt = select(func.avg(Review.rating), func.count(Review.id)).where(
            Review.deleted_at.is_(None), Review.helper_id == helper_id, Review.status == "visible"
        )
        avg_rating, count = (await db.execute(stmt)).one()
        if not count:
            return 0.0, 0
        return float(avg_rating or 0.0), int(count or 0)


review_repository = ReviewRepository()
