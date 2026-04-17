from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_address import SavedAddress
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class SavedAddressRepository(RepositoryImpl[SavedAddress]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(SavedAddress)
        super().__init__(
            model=SavedAddress,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_by_customer(self, db: AsyncSession, customer_id: str) -> list[SavedAddress]:
        rows = await db.execute(
            select(SavedAddress)
            .where(SavedAddress.deleted_at.is_(None), SavedAddress.customer_id == customer_id)
            .order_by(SavedAddress.is_default.desc(), SavedAddress.updated_at.desc())
        )
        return list(rows.scalars().all())

    async def get_by_id_and_customer(self, db: AsyncSession, address_id: str, customer_id: str) -> SavedAddress | None:
        row = await db.execute(
            select(SavedAddress).where(
                SavedAddress.deleted_at.is_(None), SavedAddress.id == address_id, SavedAddress.customer_id == customer_id
            )
        )
        return row.scalar_one_or_none()

    async def clear_default_for_customer(self, db: AsyncSession, customer_id: str, *, keep_address_id: str | None = None) -> None:
        stmt = (
            update(SavedAddress)
            .where(SavedAddress.deleted_at.is_(None), SavedAddress.customer_id == customer_id, SavedAddress.is_default.is_(True))
            .values(is_default=False)
        )
        if keep_address_id:
            stmt = stmt.where(SavedAddress.id != keep_address_id)
        await db.execute(stmt)


saved_address_repository = SavedAddressRepository()
