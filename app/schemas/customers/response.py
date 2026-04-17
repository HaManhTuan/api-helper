from datetime import datetime
from typing import Dict, Optional

from app.schemas.common.base_schema import BaseSchema


class AdminCustomerListItemResponse(BaseSchema):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    created_at: datetime


class AdminCustomerDetailResponse(BaseSchema):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    booking_counts: Dict[str, int]


class PrivacyRequestResponse(BaseSchema):
    id: str
    customer_id: str
    request_type: str
    status: str
    legal_basis: Optional[str] = None
    requested_payload: Optional[dict] = None
    resolution_summary: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
