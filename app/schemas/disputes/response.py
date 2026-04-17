from datetime import datetime
from typing import Optional

from app.schemas.common.base_schema import BaseSchema


class DisputeResponse(BaseSchema):
    id: str
    booking_id: str
    owner_staff_id: Optional[str] = None
    dispute_type: str
    status: str
    description: Optional[str] = None
    insurance_claim_id: Optional[str] = None
    opened_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class DisputeAdjustmentResponse(BaseSchema):
    id: str
    dispute_id: str
    booking_id: str
    direction: str
    target_party: str
    amount: int
    reason_code: str
    note: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
