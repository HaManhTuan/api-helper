from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.helper_document_type import HelperDocumentType
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class HelperDocumentTypeRepository(RepositoryImpl[HelperDocumentType]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(HelperDocumentType)
        super().__init__(
            model=HelperDocumentType,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[HelperDocumentType]:
        result = await db.execute(
            select(HelperDocumentType).where(
                HelperDocumentType.code == code,
                HelperDocumentType.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def list_active(self, db: AsyncSession) -> List[HelperDocumentType]:
        result = await db.execute(
            select(HelperDocumentType)
            .where(HelperDocumentType.deleted_at.is_(None), HelperDocumentType.active.is_(True))
            .order_by(HelperDocumentType.sort_order.asc(), HelperDocumentType.code.asc())
        )
        return list(result.scalars().all())

    async def list_required_codes(self, db: AsyncSession) -> List[str]:
        result = await db.execute(
            select(HelperDocumentType.code).where(
                HelperDocumentType.deleted_at.is_(None),
                HelperDocumentType.active.is_(True),
                HelperDocumentType.required.is_(True),
            )
        )
        return [code for code in result.scalars().all()]


helper_document_type_repository = HelperDocumentTypeRepository()
