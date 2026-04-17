from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class AdminCustomerListRequest(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)
    search: Optional[str] = Field(default=None, min_length=1, max_length=255)
    status: Optional[str] = Field(default=None, min_length=3, max_length=20)


class AdminCustomerStatusUpdateRequest(BaseSchema):
    reason_code: str = Field(..., min_length=2, max_length=100)
    note: Optional[str] = Field(default=None, max_length=1000)
    expected_updated_at: Optional[datetime] = None


class PrivacyRequestCreateRequest(BaseSchema):
    request_type: Literal["export", "delete", "anonymize"]
    legal_basis: Optional[str] = Field(default=None, max_length=80)
    requested_payload: Optional[Dict[str, Any]] = None


class PrivacyRequestReviewRequest(BaseSchema):
    status: Literal["in_review", "approved", "rejected", "completed", "cancelled"]
    resolution_summary: Optional[str] = Field(default=None, max_length=2000)
