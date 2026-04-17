from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class AdminAssignBookingRequest(BaseSchema):
    helper_id: str = Field(..., min_length=1, max_length=64)


class AdminReassignBookingRequest(BaseSchema):
    helper_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    reason_code: Optional[str] = Field(default=None, max_length=64)


class AdminCancelBookingRequest(BaseSchema):
    reason_code: str = Field(..., min_length=1, max_length=64)


class AdminBookingFilterRequest(BaseSchema):
    status: Optional[str] = None
    customer_id: Optional[str] = None
    helper_id: Optional[str] = None
    scheduled_from: Optional[datetime] = None
    scheduled_to: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
