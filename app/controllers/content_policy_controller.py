from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.content import ContentBlockResponse, ContentBlockUpsertRequest
from app.services.content_policy_service import content_policy_service
from app.utils.auth import require_permission

admin_router = APIRouter()
public_router = APIRouter()


def _to_response(item) -> ContentBlockResponse:
    return ContentBlockResponse(
        id=item.id,
        key=item.key,
        locale=item.locale,
        title=item.title,
        body=item.body,
        content_format=item.content_format,
        version=item.version,
        status=item.status,
        published_at=item.published_at,
        published_by=item.published_by,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@admin_router.post("/content/blocks", response_model=SuccessResponse[ContentBlockResponse])  # type: ignore[misc]
async def upsert_content_block(
    payload: ContentBlockUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("content:manage")),
) -> SuccessResponse[ContentBlockResponse]:
    row = await content_policy_service.upsert_block(db, current_user, payload)
    return ResponseBuilder.created("Content block upserted", _to_response(row))


@admin_router.get("/content/blocks", response_model=SuccessResponse[List[ContentBlockResponse]])  # type: ignore[misc]
async def list_content_blocks(
    key: Optional[str] = Query(default=None),
    locale: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("content:manage")),
) -> SuccessResponse[List[ContentBlockResponse]]:
    rows = await content_policy_service.list_blocks(db, key=key, locale=locale, status=status)
    return ResponseBuilder.success("Content blocks retrieved", [_to_response(item) for item in rows])


@public_router.get("/content/{key}", response_model=SuccessResponse[ContentBlockResponse])  # type: ignore[misc]
async def get_published_content(
    key: str,
    locale: str = Query(default="vi"),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ContentBlockResponse]:
    row = await content_policy_service.get_published(db, key=key, locale=locale)
    return ResponseBuilder.success("Published content retrieved", _to_response(row))
