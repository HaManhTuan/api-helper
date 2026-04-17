from datetime import datetime
from typing import Any, Dict, List, Optional

from app.schemas.common.base_schema import BaseSchema


class HelperProfileResponse(BaseSchema):
    id: str
    user_id: str
    display_name: str
    skills: Optional[List[str]] = None
    service_area: Dict[str, Any]
    approval_status: str
    suspension_reason_code: Optional[str] = None
    aggregate_rating: float
    ratings_count: int
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class HelperModerationDetailResponse(BaseSchema):
    helper_id: str
    role: str
    account_status: str
    email: Optional[str] = None
    phone: Optional[str] = None
    profile: HelperProfileResponse


class HelperDocumentTypeResponse(BaseSchema):
    id: str
    code: str
    name: str
    required: bool
    active: bool
    sort_order: int


class HelperDocumentResponse(BaseSchema):
    id: str
    helper_id: str
    document_type: str
    storage_ref: str
    mime_type: str
    file_size_bytes: int
    status: str
    review_reason_code: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class HelperDocumentUploadIntentResponse(BaseSchema):
    upload_url: str
    storage_ref: str
    expires_in_seconds: int
    required_headers: Dict[str, str]


class HelperEligibilityResponse(BaseSchema):
    eligible: bool
    reason_code: Optional[str] = None
    missing_required_document_types: List[str]
