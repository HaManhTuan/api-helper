from typing import Literal, Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class DisputeCreateRequest(BaseSchema):
    booking_id: str = Field(..., min_length=1, max_length=64)
    owner_staff_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    dispute_type: str = Field(..., min_length=2, max_length=40)
    description: Optional[str] = None
    insurance_claim_id: Optional[str] = Field(default=None, min_length=1, max_length=64)


class DisputeUpdateRequest(BaseSchema):
    owner_staff_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    dispute_type: Optional[str] = Field(default=None, min_length=2, max_length=40)
    status: Optional[Literal["open", "investigating", "resolved", "closed"]] = None
    description: Optional[str] = None
    insurance_claim_id: Optional[str] = Field(default=None, min_length=1, max_length=64)


class DisputeAdjustmentCreateRequest(BaseSchema):
    direction: Literal["credit", "debit"]
    target_party: Literal["customer", "helper", "platform"]
    amount: int = Field(..., ge=1)
    reason_code: str = Field(..., min_length=1, max_length=64)
    note: Optional[str] = None
