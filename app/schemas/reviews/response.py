from datetime import datetime
from typing import Optional

from app.schemas.common.base_schema import BaseSchema


class ReviewModerationResponse(BaseSchema):
    id: str
    booking_id: str
    helper_id: str
    customer_id: str
    rating: int
    comment: Optional[str] = None
    status: str
    flagged_reason_code: Optional[str] = None
    moderated_by: Optional[str] = None
    moderated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class HelperAggregateResponse(BaseSchema):
    helper_id: str
    aggregate_rating: float
    ratings_count: int
