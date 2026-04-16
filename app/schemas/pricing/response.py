from datetime import datetime
from typing import Any, Dict, List, Optional

from app.schemas.common.base_schema import BaseSchema


class ServiceOfferingResponse(BaseSchema):
    id: str
    code: str
    name: str
    description: Optional[str] = None
    unit: str
    active: bool
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class PriceBookEntryResponse(BaseSchema):
    id: str
    service_offering_id: str
    variant_code: Optional[str] = None
    zone_code: Optional[str] = None
    currency: str
    customer_price: int
    reference_cost: int
    margin: int
    effective_from: datetime
    effective_to: Optional[datetime] = None
    priority: int
    active: bool
    created_at: datetime
    updated_at: datetime


class CommissionRuleResponse(BaseSchema):
    id: str
    service_offering_id: Optional[str] = None
    helper_percent: float
    platform_percent: float
    fixed_platform_fee: int
    fixed_helper_fee: int
    effective_from: datetime
    effective_to: Optional[datetime] = None
    priority: int
    active: bool
    created_at: datetime
    updated_at: datetime


class BookingLineItemBreakdownResponse(BaseSchema):
    service_code: str
    quantity: int
    unit_price: int
    subtotal_before_tax: int
    tax_amount: int
    line_total: int
    vat_rate: float
    price_display_mode: str
    commission_base: str
    helper_earnings: int
    platform_fee: int
    applied_price_entry_id: Optional[str] = None
    applied_commission_rule_id: Optional[str] = None


class BookingFinancialSnapshotResponse(BaseSchema):
    id: str
    booking_id: str
    currency: str
    customer_total: int
    subtotal_before_tax: int
    tax_total: int
    helper_total: int
    platform_total: int
    line_items: List[BookingLineItemBreakdownResponse]
    computed_at: datetime

