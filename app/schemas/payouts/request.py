from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class PayoutBatchGenerateRequest(BaseSchema):
    period_start: datetime
    period_end: datetime
    currency: str = Field(default="VND", min_length=3, max_length=10)


class PayoutBatchMarkPaidRequest(BaseSchema):
    status: Literal["paid", "failed"]
    failure_reason: Optional[str] = Field(default=None, max_length=2000)
