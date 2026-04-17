from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.disputes import (
    DisputeAdjustmentCreateRequest,
    DisputeAdjustmentResponse,
    DisputeCreateRequest,
    DisputeResponse,
    DisputeUpdateRequest,
)
from app.services.dispute_service import dispute_service
from app.utils.auth import require_permission

router = APIRouter()


def _to_dispute_response(d) -> DisputeResponse:
    return DisputeResponse(
        id=d.id,
        booking_id=d.booking_id,
        owner_staff_id=d.owner_staff_id,
        dispute_type=d.dispute_type,
        status=d.status,
        description=d.description,
        insurance_claim_id=d.insurance_claim_id,
        opened_at=d.opened_at,
        resolved_at=d.resolved_at,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


def _to_adjustment_response(a) -> DisputeAdjustmentResponse:
    return DisputeAdjustmentResponse(
        id=a.id,
        dispute_id=a.dispute_id,
        booking_id=a.booking_id,
        direction=a.direction,
        target_party=a.target_party,
        amount=int(a.amount),
        reason_code=a.reason_code,
        note=a.note,
        created_by=a.created_by,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


@router.get("/disputes", response_model=SuccessResponse[List[DisputeResponse]])  # type: ignore[misc]
async def list_disputes(
    status: Optional[str] = Query(default=None),
    booking_id: Optional[str] = Query(default=None),
    owner_staff_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("disputes:manage")),
) -> SuccessResponse[List[DisputeResponse]]:
    rows = await dispute_service.list_disputes(
        db,
        status=status,
        booking_id=booking_id,
        owner_staff_id=owner_staff_id,
    )
    return ResponseBuilder.success("Disputes retrieved", [_to_dispute_response(r) for r in rows])


@router.post("/disputes", response_model=SuccessResponse[DisputeResponse])  # type: ignore[misc]
async def create_dispute(
    payload: DisputeCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("disputes:manage")),
) -> SuccessResponse[DisputeResponse]:
    dispute = await dispute_service.create_dispute(db, current_user, payload)
    return ResponseBuilder.created("Dispute created", _to_dispute_response(dispute))


@router.get("/disputes/{dispute_id}", response_model=SuccessResponse[DisputeResponse])  # type: ignore[misc]
async def get_dispute(
    dispute_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("disputes:manage")),
) -> SuccessResponse[DisputeResponse]:
    dispute = await dispute_service.get_dispute(db, dispute_id)
    return ResponseBuilder.success("Dispute retrieved", _to_dispute_response(dispute))


@router.put("/disputes/{dispute_id}", response_model=SuccessResponse[DisputeResponse])  # type: ignore[misc]
async def update_dispute(
    dispute_id: str,
    payload: DisputeUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("disputes:manage")),
) -> SuccessResponse[DisputeResponse]:
    dispute = await dispute_service.update_dispute(db, current_user, dispute_id, payload)
    return ResponseBuilder.updated("Dispute updated", _to_dispute_response(dispute))


@router.post("/disputes/{dispute_id}/adjustments", response_model=SuccessResponse[DisputeAdjustmentResponse])  # type: ignore[misc]
async def create_adjustment(
    dispute_id: str,
    payload: DisputeAdjustmentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("adjustments:manage")),
) -> SuccessResponse[DisputeAdjustmentResponse]:
    adjustment = await dispute_service.create_adjustment(db, current_user, dispute_id, payload)
    return ResponseBuilder.created("Dispute adjustment created", _to_adjustment_response(adjustment))


@router.get("/disputes/{dispute_id}/adjustments", response_model=SuccessResponse[List[DisputeAdjustmentResponse]])  # type: ignore[misc]
async def list_adjustments(
    dispute_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("adjustments:manage")),
) -> SuccessResponse[List[DisputeAdjustmentResponse]]:
    rows = await dispute_service.list_adjustments(db, dispute_id)
    return ResponseBuilder.success("Dispute adjustments retrieved", [_to_adjustment_response(r) for r in rows])
