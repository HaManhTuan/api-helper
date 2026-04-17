from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.helper_document import HelperDocument
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class HelperDocumentRepository(RepositoryImpl[HelperDocument]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(HelperDocument)
        super().__init__(
            model=HelperDocument,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_by_helper(self, db: AsyncSession, helper_id: str) -> List[HelperDocument]:
        result = await db.execute(
            select(HelperDocument)
            .where(HelperDocument.deleted_at.is_(None), HelperDocument.helper_id == helper_id)
            .order_by(HelperDocument.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_for_review_queue(
        self,
        db: AsyncSession,
        *,
        status: Optional[str],
        document_type: Optional[str],
        helper_id: Optional[str],
    ) -> List[HelperDocument]:
        filters = [HelperDocument.deleted_at.is_(None)]
        if status:
            filters.append(HelperDocument.status == status)
        if document_type:
            filters.append(HelperDocument.document_type == document_type)
        if helper_id:
            filters.append(HelperDocument.helper_id == helper_id)
        result = await db.execute(select(HelperDocument).where(and_(*filters)).order_by(HelperDocument.created_at.desc()))
        return list(result.scalars().all())

    async def list_approved_types(self, db: AsyncSession, helper_id: str) -> List[str]:
        result = await db.execute(
            select(HelperDocument.document_type)
            .where(
                HelperDocument.deleted_at.is_(None),
                HelperDocument.helper_id == helper_id,
                HelperDocument.status == "approved",
            )
            .distinct()
        )
        return [code for code in result.scalars().all()]


helper_document_repository = HelperDocumentRepository()
