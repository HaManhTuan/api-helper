from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insurance_product import InsuranceProduct
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class InsuranceProductRepository(RepositoryImpl[InsuranceProduct]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(InsuranceProduct)
        super().__init__(
            model=InsuranceProduct,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_products(self, db: AsyncSession, *, active: Optional[bool]) -> List[InsuranceProduct]:
        stmt = select(InsuranceProduct).where(InsuranceProduct.deleted_at.is_(None)).order_by(InsuranceProduct.updated_at.desc())
        if active is not None:
            stmt = stmt.where(InsuranceProduct.active == active)
        rows = await db.execute(stmt)
        return list(rows.scalars().all())


insurance_product_repository = InsuranceProductRepository()
