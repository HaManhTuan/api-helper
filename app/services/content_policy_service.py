from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException, ValidationException
from app.models.content_block import ContentBlock
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User
from app.repositories.concrete.content_block_repository import content_block_repository


class ContentPolicyService:
    VALID_STATUS = {"draft", "published", "archived"}

    async def upsert_block(self, db: AsyncSession, actor: User, payload) -> ContentBlock:
        blocks = await content_block_repository.list_blocks(db, key=payload.key, locale=payload.locale, status=None)
        target = next((x for x in blocks if x.version == payload.version), None)
        if target is None:
            target = ContentBlock(key=payload.key, locale=payload.locale, version=payload.version, body=payload.body)

        if payload.status not in self.VALID_STATUS:
            raise ValidationException("Invalid content status")

        target.title = payload.title
        target.body = payload.body
        target.content_format = payload.content_format
        target.status = payload.status
        if payload.status == "published":
            target.published_at = datetime.utcnow()
            target.published_by = actor.id

        db.add(target)
        await db.flush()
        await self._audit(db, actor.id, actor.id, "content:upsert", f"key={target.key};locale={target.locale};status={target.status}")
        await db.commit()
        await db.refresh(target)
        return target

    async def list_blocks(self, db: AsyncSession, *, key: Optional[str], locale: Optional[str], status: Optional[str]) -> List[ContentBlock]:
        return await content_block_repository.list_blocks(db, key=key, locale=locale, status=status)

    async def get_published(self, db: AsyncSession, *, key: str, locale: str) -> ContentBlock:
        block = await content_block_repository.get_latest_published(db, key=key, locale=locale)
        if block is None and locale != "vi":
            block = await content_block_repository.get_latest_published(db, key=key, locale="vi")
        if block is None:
            raise NotFoundException("Published content not found")
        return block

    async def _audit(self, db: AsyncSession, actor_user_id: str, target_user_id: str, action: str, details: str) -> None:
        db.add(
            StaffAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action=action,
                details=details,
            )
        )


content_policy_service = ContentPolicyService()
