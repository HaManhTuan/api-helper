from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer_quote import CustomerQuote
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class CustomerQuoteRepository(RepositoryImpl[CustomerQuote]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(CustomerQuote)
        super().__init__(
            model=CustomerQuote,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def get_active_by_code(self, db: AsyncSession, customer_id: str, quote_code: str, at: datetime) -> CustomerQuote | None:
        row = await db.execute(
            select(CustomerQuote).where(
                CustomerQuote.deleted_at.is_(None),
                CustomerQuote.customer_id == customer_id,
                CustomerQuote.quote_code == quote_code,
                CustomerQuote.expires_at >= at,
            )
        )
        return row.scalar_one_or_none()


customer_quote_repository = CustomerQuoteRepository()
