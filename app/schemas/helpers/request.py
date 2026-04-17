from datetime import datetime
from typing import List, Literal, Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class HelperDocumentTypeUpsertRequest(BaseSchema):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=120)
    required: bool = False
    active: bool = True
    sort_order: int = Field(default=0, ge=0)


class HelperDocumentUploadIntentRequest(BaseSchema):
    document_type: str = Field(..., min_length=2, max_length=50)
    mime_type: Literal["image/jpeg", "image/png", "application/pdf"]
    file_size_bytes: int = Field(..., ge=1, le=10 * 1024 * 1024)
    file_name: str = Field(..., min_length=1, max_length=255)


class HelperDocumentSubmitRequest(BaseSchema):
    document_type: str = Field(..., min_length=2, max_length=50)
    storage_ref: str = Field(..., min_length=1, max_length=2048)
    mime_type: Literal["image/jpeg", "image/png", "application/pdf"]
    file_size_bytes: int = Field(..., ge=1, le=10 * 1024 * 1024)


class HelperDocumentReviewRequest(BaseSchema):
    status: Literal["approved", "rejected", "needs_more_info"]
    review_reason_code: Optional[str] = Field(default=None, max_length=64)


class HelperModerationActionRequest(BaseSchema):
    reason_code: Optional[str] = Field(default=None, max_length=64)


class HelperProfileUpsertRequest(BaseSchema):
    display_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    skills: Optional[List[str]] = None
    service_area: Optional[dict] = None
    approved_at: Optional[datetime] = None
