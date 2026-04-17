from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class InsuranceProductUpsertRequest(BaseSchema):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    coverage_summary: str = Field(..., min_length=2)
    premium_model: str = Field(..., min_length=2, max_length=40)
    eligibility_rule: str = Field(default="approved_helpers_only", min_length=2, max_length=80)
    active: bool = True
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class InsuranceEnrollmentUpsertRequest(BaseSchema):
    helper_id: str = Field(..., min_length=1, max_length=64)
    product_id: str = Field(..., min_length=1, max_length=64)
    status: str = Field(..., min_length=3, max_length=20)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    notes: Optional[str] = None


class InsuranceClaimCreateRequest(BaseSchema):
    booking_id: str = Field(..., min_length=1, max_length=64)
    reporter_role: str = Field(..., min_length=3, max_length=20)
    description: str = Field(..., min_length=2)
    severity: str = Field(default="medium", min_length=2, max_length=20)


class InsuranceClaimUpdateRequest(BaseSchema):
    status: Optional[str] = Field(default=None, min_length=2, max_length=30)
    resolution_notes: Optional[str] = None
    payout_amount: Optional[int] = Field(default=None, ge=0)


class ServiceInsuranceRuleUpdateRequest(BaseSchema):
    insurance_required: bool
    insurance_enforcement: str = Field(default="hard", min_length=4, max_length=20)
