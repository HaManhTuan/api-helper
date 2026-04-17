from typing import Any, Dict, Literal, Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class CustomerPrivacyRequestCreateRequest(BaseSchema):
    request_type: Literal["export", "delete", "anonymize"]
    legal_basis: Optional[str] = Field(default=None, max_length=80)
    requested_payload: Optional[Dict[str, Any]] = None
