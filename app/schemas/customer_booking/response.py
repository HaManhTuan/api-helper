from datetime import datetime
from typing import Optional

from app.schemas.bookings.response import BookingResponse
from app.schemas.common.base_schema import BaseSchema
from app.schemas.pricing.response import BookingLineItemBreakdownResponse


class CustomerQuoteResponse(BaseSchema):
    quote_id: str
    currency: str
    subtotal_before_tax: int
    tax_total: int
    promotion_total: int
    customer_total: int
    line_items: list[BookingLineItemBreakdownResponse]
    expires_at: datetime


class CustomerBookingDetailResponse(BookingResponse):
    financial_snapshot: Optional[dict] = None
