from datetime import datetime
from typing import Optional

from app.schemas.common.base_schema import BaseSchema


class PromotionResponse(BaseSchema):
    id: str
    code: str
    promotion_type: str
    service_id: Optional[str] = None
    discount_percent: Optional[float] = None
    discount_amount: Optional[int] = None
    max_redemptions: Optional[int] = None
    per_user_limit: Optional[int] = None
    stack_rule: str
    effective_from: datetime
    effective_to: Optional[datetime] = None
    active: bool
    created_at: datetime
    updated_at: datetime


class PromotionPerformanceResponse(BaseSchema):
    promotion_id: str
    code: str
    total_redemptions: int
    consumed_redemptions: int
    gmv_with_promotion: int
    estimated_discount_cost: int
