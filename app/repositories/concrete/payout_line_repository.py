from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.booking_financial_snapshot import BookingFinancialSnapshot
from app.models.dispute_adjustment import DisputeAdjustment
from app.models.payout_line import PayoutLine
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class PayoutLineRepository(RepositoryImpl[PayoutLine]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(PayoutLine)
        super().__init__(
            model=PayoutLine,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_by_batch(self, db: AsyncSession, *, payout_batch_id: str) -> List[PayoutLine]:
        result = await db.execute(
            select(PayoutLine)
            .where(PayoutLine.deleted_at.is_(None), PayoutLine.payout_batch_id == payout_batch_id)
            .order_by(PayoutLine.total_amount.desc(), PayoutLine.created_at.asc())
        )
        return list(result.scalars().all())

    async def aggregate_base_amounts(
        self, db: AsyncSession, *, period_start: datetime, period_end: datetime
    ) -> Dict[str, dict]:
        stmt = (
            select(
                Booking.helper_id,
                func.sum(BookingFinancialSnapshot.helper_total),
                func.array_agg(Booking.id),
                func.count(Booking.id),
            )
            .join(Booking, Booking.id == BookingFinancialSnapshot.booking_id)
            .where(
                BookingFinancialSnapshot.deleted_at.is_(None),
                Booking.deleted_at.is_(None),
                Booking.status == "completed",
                Booking.helper_id.is_not(None),
                and_(
                    BookingFinancialSnapshot.computed_at >= period_start,
                    BookingFinancialSnapshot.computed_at < period_end,
                ),
            )
            .group_by(Booking.helper_id)
        )
        rows = await db.execute(stmt)
        data: Dict[str, dict] = {}
        for helper_id, amount, booking_ids, booking_count in rows.all():
            if helper_id is None:
                continue
            data[str(helper_id)] = {
                "base_amount": int(amount or 0),
                "booking_ids": [str(i) for i in (booking_ids or [])],
                "booking_count": int(booking_count or 0),
            }
        return data

    async def aggregate_adjustments(
        self, db: AsyncSession, *, period_start: datetime, period_end: datetime
    ) -> Dict[str, int]:
        signed_amount = case(
            (DisputeAdjustment.direction == "credit", DisputeAdjustment.amount),
            else_=-DisputeAdjustment.amount,
        )
        stmt = (
            select(Booking.helper_id, func.sum(signed_amount))
            .join(Booking, Booking.id == DisputeAdjustment.booking_id)
            .where(
                DisputeAdjustment.deleted_at.is_(None),
                Booking.deleted_at.is_(None),
                Booking.helper_id.is_not(None),
                DisputeAdjustment.target_party == "helper",
                and_(DisputeAdjustment.created_at >= period_start, DisputeAdjustment.created_at < period_end),
            )
            .group_by(Booking.helper_id)
        )
        rows = await db.execute(stmt)
        result: Dict[str, int] = defaultdict(int)
        for helper_id, amount in rows.all():
            if helper_id is None:
                continue
            result[str(helper_id)] = int(amount or 0)
        return dict(result)


payout_line_repository = PayoutLineRepository()
