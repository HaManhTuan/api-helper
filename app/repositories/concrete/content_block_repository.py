from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_block import ContentBlock
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class ContentBlockRepository(RepositoryImpl[ContentBlock]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(ContentBlock)
        super().__init__(
            model=ContentBlock,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )

    async def list_blocks(self, db: AsyncSession, *, key: Optional[str], locale: Optional[str], status: Optional[str]) -> List[ContentBlock]:
        stmt = select(ContentBlock).where(ContentBlock.deleted_at.is_(None))
        if key:
            stmt = stmt.where(ContentBlock.key == key)
        if locale:
            stmt = stmt.where(ContentBlock.locale == locale)
        if status:
            stmt = stmt.where(ContentBlock.status == status)
        stmt = stmt.order_by(ContentBlock.updated_at.desc())
        rows = await db.execute(stmt)
        return list(rows.scalars().all())

    async def get_latest_published(self, db: AsyncSession, *, key: str, locale: str) -> Optional[ContentBlock]:
        stmt = (
            select(ContentBlock)
            .where(
                ContentBlock.deleted_at.is_(None),
                ContentBlock.key == key,
                ContentBlock.locale == locale,
                ContentBlock.status == "published",
                ContentBlock.published_at.is_not(None),
            )
            .order_by(ContentBlock.published_at.desc(), ContentBlock.updated_at.desc())
            .limit(1)
        )
        return (await db.execute(stmt)).scalar_one_or_none()


content_block_repository = ContentBlockRepository()
