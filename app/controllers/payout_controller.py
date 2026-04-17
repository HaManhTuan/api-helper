from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.payouts import (
    PayoutBatchDetailResponse,
    PayoutBatchGenerateRequest,
    PayoutBatchMarkPaidRequest,
    PayoutBatchResponse,
    PayoutExportResponse,
    PayoutLineResponse,
)
from app.services.payout_service import payout_service
from app.utils.auth import require_permission

router = APIRouter()


def _to_batch_response(item) -> PayoutBatchResponse:
    return PayoutBatchResponse(
        id=item.id,
        period_start=item.period_start,
        period_end=item.period_end,
        status=item.status,
        currency=item.currency,
        total_lines=int(item.total_lines),
        total_amount=int(item.total_amount),
        approved_by=item.approved_by,
        approved_at=item.approved_at,
        paid_by=item.paid_by,
        paid_at=item.paid_at,
        failure_reason=item.failure_reason,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _to_line_response(item) -> PayoutLineResponse:
    return PayoutLineResponse(
        id=item.id,
        payout_batch_id=item.payout_batch_id,
        helper_id=item.helper_id,
        currency=item.currency,
        base_amount=int(item.base_amount),
        adjustment_amount=int(item.adjustment_amount),
        total_amount=int(item.total_amount),
        booking_ids=[str(v) for v in (item.booking_ids or [])],
        booking_count=int(item.booking_count),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("/payouts/batches/generate", response_model=SuccessResponse[PayoutBatchResponse])  # type: ignore[misc]
async def generate_batch(
    payload: PayoutBatchGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payouts:generate")),
) -> SuccessResponse[PayoutBatchResponse]:
    batch = await payout_service.generate_batch(db, current_user, payload)
    return ResponseBuilder.created("Payout batch generated", _to_batch_response(batch))


@router.get("/payouts/batches", response_model=SuccessResponse[List[PayoutBatchResponse]])  # type: ignore[misc]
async def list_batches(
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("payouts:read")),
) -> SuccessResponse[List[PayoutBatchResponse]]:
    rows = await payout_service.list_batches(db, status=status)
    return ResponseBuilder.success("Payout batches retrieved", [_to_batch_response(item) for item in rows])


@router.get("/payouts/batches/{batch_id}", response_model=SuccessResponse[PayoutBatchDetailResponse])  # type: ignore[misc]
async def get_batch_detail(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("payouts:read")),
) -> SuccessResponse[PayoutBatchDetailResponse]:
    batch, lines = await payout_service.get_batch_detail(db, batch_id)
    return ResponseBuilder.success(
        "Payout batch retrieved",
        PayoutBatchDetailResponse(**_to_batch_response(batch).model_dump(), lines=[_to_line_response(item) for item in lines]),
    )


@router.post("/payouts/batches/{batch_id}/approve", response_model=SuccessResponse[PayoutBatchResponse])  # type: ignore[misc]
async def approve_batch(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payouts:approve")),
) -> SuccessResponse[PayoutBatchResponse]:
    batch = await payout_service.approve_batch(db, current_user, batch_id)
    return ResponseBuilder.updated("Payout batch approved", _to_batch_response(batch))


@router.get("/payouts/batches/{batch_id}/export", response_model=SuccessResponse[PayoutExportResponse])  # type: ignore[misc]
async def export_batch(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("payouts:read")),
) -> SuccessResponse[PayoutExportResponse]:
    result = await payout_service.export_batch_csv(db, batch_id)
    return ResponseBuilder.success("Payout batch exported", PayoutExportResponse(**result))


@router.post("/payouts/batches/{batch_id}/mark-paid", response_model=SuccessResponse[PayoutBatchResponse])  # type: ignore[misc]
async def mark_batch_paid(
    batch_id: str,
    payload: PayoutBatchMarkPaidRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payouts:mark_paid")),
) -> SuccessResponse[PayoutBatchResponse]:
    batch = await payout_service.mark_batch_paid(db, current_user, batch_id, payload)
    return ResponseBuilder.updated("Payout batch status updated", _to_batch_response(batch))
