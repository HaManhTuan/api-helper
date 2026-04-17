from datetime import datetime
from typing import Optional

from app.schemas.common.base_schema import BaseSchema


class InsuranceProductResponse(BaseSchema):
    id: str
    name: str
    description: Optional[str] = None
    coverage_summary: str
    premium_model: str
    eligibility_rule: str
    active: bool
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class InsuranceEnrollmentResponse(BaseSchema):
    id: str
    helper_id: str
    product_id: str
    status: str
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class InsuranceClaimResponse(BaseSchema):
    id: str
    booking_id: str
    reporter_role: str
    description: str
    severity: str
    status: str
    resolution_notes: Optional[str] = None
    payout_amount: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ServiceInsuranceRuleResponse(BaseSchema):
    service_id: str
    insurance_required: bool
    insurance_enforcement: str
