from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.exceptions import NotFoundException
from app.models.user import User
from app.schemas.analytics import (
    BookingTimeseriesPointResponse,
    CohortMetricsResponse,
    ReportExportJobResponse,
    ReportExportRequest,
    RevenueReportResponse,
    SupplyDemandKpiResponse,
)
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.services.analytics_service import analytics_service
from app.utils.auth import require_permission

router = APIRouter()


@router.get("/analytics/bookings-timeseries", response_model=SuccessResponse[List[BookingTimeseriesPointResponse]])  # type: ignore[misc]
async def bookings_timeseries(
    start_at: datetime = Query(...),
    end_at: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("analytics:read")),
) -> SuccessResponse[List[BookingTimeseriesPointResponse]]:
    rows = await analytics_service.bookings_timeseries(db, start_at=start_at, end_at=end_at)
    return ResponseBuilder.success("Booking timeseries retrieved", [BookingTimeseriesPointResponse(**item) for item in rows])


@router.get("/analytics/supply-demand-kpis", response_model=SuccessResponse[SupplyDemandKpiResponse])  # type: ignore[misc]
async def supply_demand_kpis(
    start_at: datetime = Query(...),
    end_at: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("analytics:read")),
) -> SuccessResponse[SupplyDemandKpiResponse]:
    row = await analytics_service.supply_demand_kpis(db, start_at=start_at, end_at=end_at)
    return ResponseBuilder.success("Supply-demand KPIs retrieved", SupplyDemandKpiResponse(**row))


@router.get("/analytics/revenue", response_model=SuccessResponse[RevenueReportResponse])  # type: ignore[misc]
async def revenue_report(
    start_at: datetime = Query(...),
    end_at: datetime = Query(...),
    group_by: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("analytics:read")),
) -> SuccessResponse[RevenueReportResponse]:
    report = await analytics_service.revenue_report(db, start_at=start_at, end_at=end_at, group_by=group_by)
    return ResponseBuilder.success("Revenue report retrieved", RevenueReportResponse(**report))


@router.get("/analytics/cohort", response_model=SuccessResponse[CohortMetricsResponse])  # type: ignore[misc]
async def cohort_metrics(
    start_at: datetime = Query(...),
    end_at: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("analytics:read")),
) -> SuccessResponse[CohortMetricsResponse]:
    row = await analytics_service.cohort_metrics(db, start_at=start_at, end_at=end_at)
    return ResponseBuilder.success("Cohort metrics retrieved", CohortMetricsResponse(**row))


@router.post("/analytics/exports", response_model=SuccessResponse[ReportExportJobResponse], status_code=status.HTTP_202_ACCEPTED)  # type: ignore[misc]
async def create_export_job(
    payload: ReportExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("reports:export")),
) -> JSONResponse:
    job = await analytics_service.create_export_job(db, actor=current_user, payload=payload)
    response = ResponseBuilder.success(
        "Export job submitted",
        ReportExportJobResponse(
            id=job.id,
            report_type=job.report_type,
            status=job.status,
            file_ref=job.file_ref,
            checksum=job.checksum,
            error_message=job.error_message,
            created_at=job.created_at,
            completed_at=job.completed_at,
        ),
        meta={"poll_url": f"/api/v1/admin/analytics/exports/{job.id}"},
    )
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=response.model_dump(mode="json"))


@router.get("/analytics/exports/{job_id}", response_model=SuccessResponse[ReportExportJobResponse])  # type: ignore[misc]
async def get_export_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("reports:export")),
) -> SuccessResponse[ReportExportJobResponse]:
    job = await analytics_service.get_export_job(db, job_id)
    if job is None:
        raise NotFoundException("Report export job not found")
    return ResponseBuilder.success(
        "Export job retrieved",
        ReportExportJobResponse(
            id=job.id,
            report_type=job.report_type,
            status=job.status,
            file_ref=job.file_ref,
            checksum=job.checksum,
            error_message=job.error_message,
            created_at=job.created_at,
            completed_at=job.completed_at,
        ),
    )
