from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class ReviewModerationFilterRequest(BaseSchema):
    booking_id: Optional[str] = Field(default=None, max_length=64)
    helper_id: Optional[str] = Field(default=None, max_length=64)
    customer_id: Optional[str] = Field(default=None, max_length=64)
    min_rating: Optional[int] = Field(default=None, ge=1, le=5)
    max_rating: Optional[int] = Field(default=None, ge=1, le=5)
    status: Optional[Literal["visible", "hidden", "flagged"]] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


class ReviewModerationActionRequest(BaseSchema):
    action: Literal["hide", "unhide", "flag"]
    reason_code: Optional[str] = Field(default=None, min_length=1, max_length=64)


class ReviewAggregateOverrideRequest(BaseSchema):
    aggregate_rating: float = Field(..., ge=0.0, le=5.0)
    ratings_count: int = Field(..., ge=0)
    reason_code: str = Field(..., min_length=1, max_length=64)
