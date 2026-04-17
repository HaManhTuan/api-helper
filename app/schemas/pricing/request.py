from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class ServiceOfferingCreateRequest(BaseSchema):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    unit: str = Field(default="hour", min_length=1, max_length=50)
    active: bool = True
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ServiceOfferingUpdateRequest(BaseSchema):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = None
    unit: Optional[str] = Field(default=None, min_length=1, max_length=50)
    active: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PriceBookEntryUpsertRequest(BaseSchema):
    service_code: str = Field(..., min_length=2, max_length=50)
    variant_code: Optional[str] = Field(default=None, max_length=50)
    zone_code: Optional[str] = Field(default=None, max_length=50)

    customer_price: int = Field(..., ge=0)
    reference_cost: int = Field(default=0, ge=0)
    currency: str = Field(default="VND", min_length=3, max_length=10)

    effective_from: datetime
    effective_to: Optional[datetime] = None
    priority: int = Field(default=0, ge=0)
    active: bool = True


class CommissionRuleUpsertRequest(BaseSchema):
    service_code: Optional[str] = Field(default=None, max_length=50)  # null = default catch-all
    helper_percent: float = Field(default=0, ge=0, le=100)
    platform_percent: float = Field(default=0, ge=0, le=100)
    fixed_platform_fee: int = Field(default=0, ge=0)
    fixed_helper_fee: int = Field(default=0, ge=0)
    effective_from: datetime
    effective_to: Optional[datetime] = None
    priority: int = Field(default=0, ge=0)
    active: bool = True


class BookingLineItemPriceRequest(BaseSchema):
    service_code: str
    quantity: int = Field(default=1, ge=1)
    zone_code: Optional[str] = None
    variant_code: Optional[str] = None


class BookingSnapshotComputeRequest(BaseSchema):
    booking_id: str = Field(..., min_length=1, max_length=64)
    customer_id: str = Field(..., min_length=1, max_length=64)
    at: datetime
    quote_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    promotion_code: Optional[str] = Field(default=None, max_length=64)
    surge_multiplier: float = Field(default=1.0, ge=1.0, le=5.0)
    line_items: List[BookingLineItemPriceRequest]

