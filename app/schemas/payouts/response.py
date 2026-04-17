from datetime import datetime
from typing import List, Optional

from app.schemas.common.base_schema import BaseSchema


class PayoutLineResponse(BaseSchema):
    id: str
    payout_batch_id: str
    helper_id: str
    currency: str
    base_amount: int
    adjustment_amount: int
    total_amount: int
    booking_ids: List[str]
    booking_count: int
    created_at: datetime
    updated_at: datetime


class PayoutBatchResponse(BaseSchema):
    id: str
    period_start: datetime
    period_end: datetime
    status: str
    currency: str
    total_lines: int
    total_amount: int
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    paid_by: Optional[str] = None
    paid_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PayoutBatchDetailResponse(PayoutBatchResponse):
    lines: List[PayoutLineResponse]


class PayoutExportResponse(BaseSchema):
    payout_batch_id: str
    filename: str
    csv_content: str
