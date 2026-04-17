from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.reviews import (
    HelperAggregateResponse,
    ReviewAggregateOverrideRequest,
    ReviewModerationActionRequest,
    ReviewModerationFilterRequest,
    ReviewModerationResponse,
)
from app.services.review_moderation_service import review_moderation_service
from app.utils.auth import require_permission

router = APIRouter()


def _to_review_response(item) -> ReviewModerationResponse:
    return ReviewModerationResponse(
        id=item.id,
        booking_id=item.booking_id,
        helper_id=item.helper_id,
        customer_id=item.customer_id,
        rating=int(item.rating),
        comment=item.comment,
        status=item.status,
        flagged_reason_code=item.flagged_reason_code,
        moderated_by=item.moderated_by,
        moderated_at=item.moderated_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/reviews", response_model=SuccessResponse[List[ReviewModerationResponse]])  # type: ignore[misc]
async def list_reviews(
    booking_id: Optional[str] = Query(default=None),
    helper_id: Optional[str] = Query(default=None),
    customer_id: Optional[str] = Query(default=None),
    min_rating: Optional[int] = Query(default=None, ge=1, le=5),
    max_rating: Optional[int] = Query(default=None, ge=1, le=5),
    status: Optional[str] = Query(default=None),
    created_from: Optional[datetime] = Query(default=None),
    created_to: Optional[datetime] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("reviews:moderate")),
) -> SuccessResponse[List[ReviewModerationResponse]]:
    payload = ReviewModerationFilterRequest(
        booking_id=booking_id,
        helper_id=helper_id,
        customer_id=customer_id,
        min_rating=min_rating,
        max_rating=max_rating,
        status=status,  # type: ignore[arg-type]
        created_from=created_from,
        created_to=created_to,
        skip=skip,
        limit=limit,
    )
    rows = await review_moderation_service.list_reviews(db, payload)
    return ResponseBuilder.success("Reviews retrieved", [_to_review_response(item) for item in rows])


@router.put("/reviews/{review_id}/moderate", response_model=SuccessResponse[ReviewModerationResponse])  # type: ignore[misc]
async def moderate_review(
    review_id: str,
    payload: ReviewModerationActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("reviews:moderate")),
) -> SuccessResponse[ReviewModerationResponse]:
    review = await review_moderation_service.moderate_review(db, current_user, review_id, payload)
    return ResponseBuilder.updated("Review moderated", _to_review_response(review))


@router.post("/reviews/helpers/{helper_id}/aggregate/override", response_model=SuccessResponse[HelperAggregateResponse])  # type: ignore[misc]
async def override_helper_aggregate(
    helper_id: str,
    payload: ReviewAggregateOverrideRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("reviews:moderate")),
) -> SuccessResponse[HelperAggregateResponse]:
    profile = await review_moderation_service.override_helper_aggregate(db, current_user, helper_id, payload)
    return ResponseBuilder.updated(
        "Helper aggregate overridden",
        HelperAggregateResponse(
            helper_id=profile.user_id,
            aggregate_rating=float(profile.aggregate_rating),
            ratings_count=int(profile.ratings_count),
        ),
    )
