from datetime import datetime
from typing import List, Optional

from app.schemas.common.base_schema import BaseSchema


class BookingTimeseriesPointResponse(BaseSchema):
    date: str
    created: int
    completed: int
    cancelled: int


class SupplyDemandKpiResponse(BaseSchema):
    active_helpers: int
    new_registrations: int
    accept_rate: float
    completion_rate: float
    median_response_seconds: Optional[float] = None


class RevenueSummaryResponse(BaseSchema):
    gmv_total: int
    platform_fee_total: int
    helper_earnings_total: int
    promotion_cost_total: int


class RevenueGroupRowResponse(BaseSchema):
    key: str
    gmv_total: int
    platform_fee_total: int
    helper_earnings_total: int
    promotion_cost_total: int


class RevenueReportResponse(BaseSchema):
    summary: RevenueSummaryResponse
    groups: List[RevenueGroupRowResponse]


class CohortMetricsResponse(BaseSchema):
    signup_to_first_booking_rate: float
    repeat_customer_rate_monthly: float


class ReportExportJobResponse(BaseSchema):
    id: str
    report_type: str
    status: str
    file_ref: Optional[str] = None
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
