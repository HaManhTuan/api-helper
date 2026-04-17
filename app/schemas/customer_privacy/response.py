from datetime import datetime
from typing import Optional

from app.schemas.common.base_schema import BaseSchema


class CustomerPrivacyRequestResponse(BaseSchema):
    id: str
    request_type: str
    status: str
    legal_basis: Optional[str] = None
    requested_payload: Optional[dict] = None
    resolution_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str] = None
