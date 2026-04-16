from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class TaxRuleUpsertRequest(BaseSchema):
    service_code: Optional[str] = None  # null = global
    vat_rate: float = Field(default=0, ge=0, le=100)
    price_display_mode: str = Field(default="inclusive")  # inclusive | exclusive
    commission_base: str = Field(default="before_vat")  # before_vat | after_vat
    rounding_mode: str = Field(default="half_up")
    effective_from: datetime
    effective_to: Optional[datetime] = None
    priority: int = Field(default=0, ge=0)
    active: bool = True


class TaxConfigUpsertRequest(BaseSchema):
    platform_tax_id: Optional[str] = None

