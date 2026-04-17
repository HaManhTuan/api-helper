from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema
from app.schemas.pricing.request import BookingLineItemPriceRequest


class CustomerQuoteRequest(BaseSchema):
    scheduled_start: datetime
    address_snapshot: dict
    promotion_code: Optional[str] = Field(default=None, max_length=64)
    surge_multiplier: float = Field(default=1.0, ge=1.0, le=5.0)
    line_items: list[BookingLineItemPriceRequest]


class CustomerBookingCreateRequest(BaseSchema):
    quote_id: str = Field(..., min_length=1, max_length=64)
    scheduled_start: datetime
    scheduled_end: Optional[datetime] = None
    address_snapshot: dict
    line_items: list[BookingLineItemPriceRequest]


class CustomerBookingCancelRequest(BaseSchema):
    reason_code: str = Field(..., min_length=1, max_length=64)
