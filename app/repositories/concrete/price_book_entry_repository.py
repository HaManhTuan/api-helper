from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_book_entry import PriceBookEntry
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class PriceBookEntryRepository(RepositoryImpl[PriceBookEntry]):
    def __init__(self) -> None:
        unified_repo = repository_factory.create_repository(PriceBookEntry)
        super().__init__(
            model=PriceBookEntry,
            query_builder=unified_repo.query_builder,
            optimistic_lock_validator=unified_repo.optimistic_lock_validator,
        )

    async def list_for_service(self, db: AsyncSession, service_offering_id: str) -> List[PriceBookEntry]:
        result = await db.execute(
            select(PriceBookEntry)
            .where(PriceBookEntry.service_offering_id == service_offering_id, PriceBookEntry.deleted_at.is_(None))
            .order_by(PriceBookEntry.priority.desc(), PriceBookEntry.effective_from.desc())
        )
        return list(result.scalars().all())

    async def resolve_active(
        self,
        db: AsyncSession,
        *,
        service_offering_id: str,
        at: datetime,
        zone_code: Optional[str],
        variant_code: Optional[str],
    ) -> Optional[PriceBookEntry]:
        base_filters = [
            PriceBookEntry.deleted_at.is_(None),
            PriceBookEntry.active.is_(True),
            PriceBookEntry.service_offering_id == service_offering_id,
            PriceBookEntry.effective_from <= at,
            or_(PriceBookEntry.effective_to.is_(None), PriceBookEntry.effective_to > at),
        ]

        variant_filters = [
            or_(PriceBookEntry.variant_code.is_(None), PriceBookEntry.variant_code == variant_code),
        ]

        stmt = select(PriceBookEntry).where(and_(*base_filters, *variant_filters))

        # Deterministic fallback: zone match first, then no-zone.
        if zone_code:
            stmt = stmt.where(or_(PriceBookEntry.zone_code == zone_code, PriceBookEntry.zone_code.is_(None)))
            stmt = stmt.order_by(
                (PriceBookEntry.zone_code == zone_code).desc(),
                PriceBookEntry.priority.desc(),
                PriceBookEntry.effective_from.desc(),
            )
        else:
            stmt = stmt.where(PriceBookEntry.zone_code.is_(None))
            stmt = stmt.order_by(PriceBookEntry.priority.desc(), PriceBookEntry.effective_from.desc())

        result = await db.execute(stmt.limit(1))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]


price_book_entry_repository = PriceBookEntryRepository()

