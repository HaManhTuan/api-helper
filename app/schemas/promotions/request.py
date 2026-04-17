from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class PromotionUpsertRequest(BaseSchema):
    code: str = Field(..., min_length=3, max_length=64)
    promotion_type: Literal["percent", "fixed"]
    service_code: Optional[str] = Field(default=None, max_length=50)

    discount_percent: Optional[float] = Field(default=None, gt=0, le=100)
    discount_amount: Optional[int] = Field(default=None, ge=1)

    max_redemptions: Optional[int] = Field(default=None, ge=1)
    per_user_limit: Optional[int] = Field(default=None, ge=1)
    stack_rule: Literal["no_stack_with_surge", "promotion_then_surge", "surge_then_promotion"] = "surge_then_promotion"

    effective_from: datetime
    effective_to: Optional[datetime] = None
    active: bool = True


class PromotionRedeemPreviewRequest(BaseSchema):
    customer_id: str = Field(..., min_length=1, max_length=64)
    booking_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    quote_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    code: str = Field(..., min_length=3, max_length=64)
    service_code: Optional[str] = Field(default=None, max_length=50)
    subtotal_amount: int = Field(..., ge=0)
    surge_multiplier: float = Field(default=1.0, ge=1.0, le=5.0)
    at: datetime
