from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class BookingRepository(RepositoryImpl[Booking]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(Booking)
        super().__init__(
            model=Booking,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_with_filters(
        self,
        db: AsyncSession,
        *,
        status: Optional[str],
        customer_id: Optional[str],
        helper_id: Optional[str],
        scheduled_from: Optional[datetime],
        scheduled_to: Optional[datetime],
        skip: int,
        limit: int,
    ) -> List[Booking]:
        filters = [Booking.deleted_at.is_(None)]
        if status:
            filters.append(Booking.status == status)
        if customer_id:
            filters.append(Booking.customer_id == customer_id)
        if helper_id:
            filters.append(Booking.helper_id == helper_id)
        if scheduled_from:
            filters.append(Booking.scheduled_start >= scheduled_from)
        if scheduled_to:
            filters.append(Booking.scheduled_start <= scheduled_to)

        stmt = (
            select(Booking)
            .where(and_(*filters))
            .order_by(Booking.scheduled_start.desc(), Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_customer(
        self,
        db: AsyncSession,
        *,
        customer_id: str,
        status: Optional[str],
        skip: int,
        limit: int,
    ) -> List[Booking]:
        filters = [Booking.deleted_at.is_(None), Booking.customer_id == customer_id]
        if status:
            filters.append(Booking.status == status)
        stmt = (
            select(Booking)
            .where(and_(*filters))
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_and_customer(self, db: AsyncSession, booking_id: str, customer_id: str) -> Booking | None:
        row = await db.execute(
            select(Booking).where(
                Booking.deleted_at.is_(None),
                Booking.id == booking_id,
                Booking.customer_id == customer_id,
            )
        )
        return row.scalar_one_or_none()


booking_repository = BookingRepository()
