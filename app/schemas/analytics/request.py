from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class AnalyticsDateRangeRequest(BaseSchema):
    start_at: datetime
    end_at: datetime


class RevenueReportRequest(BaseSchema):
    start_at: datetime
    end_at: datetime
    group_by: Optional[str] = Field(default=None, max_length=20)  # service/district


class ReportExportRequest(BaseSchema):
    report_type: str = Field(..., min_length=3, max_length=40)
    start_at: datetime
    end_at: datetime
