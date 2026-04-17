from datetime import datetime
from typing import Any, Dict, Optional

from app.schemas.common.base_schema import BaseSchema


class BookingResponse(BaseSchema):
    id: str
    customer_id: str
    helper_id: Optional[str] = None
    quote_id: str
    status: str
    scheduled_start: datetime
    scheduled_end: Optional[datetime] = None
    address_snapshot: Dict[str, Any]
    reassignment_reason_code: Optional[str] = None
    cancellation_reason_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime
