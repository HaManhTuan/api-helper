from datetime import datetime
from typing import Optional

from app.schemas.common.base_schema import BaseSchema


class TaxRuleResponse(BaseSchema):
    id: str
    service_offering_id: Optional[str] = None
    vat_rate: float
    price_display_mode: str
    commission_base: str
    rounding_mode: str
    effective_from: datetime
    effective_to: Optional[datetime] = None
    priority: int
    active: bool
    created_at: datetime
    updated_at: datetime


class TaxConfigResponse(BaseSchema):
    platform_tax_id: Optional[str] = None

