from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.bookings import (
    AdminAssignBookingRequest,
    AdminBookingFilterRequest,
    AdminCancelBookingRequest,
    AdminReassignBookingRequest,
    BookingResponse,
)
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.services.booking_operations_service import booking_operations_service
from app.utils.auth import require_permission

router = APIRouter()


def _to_response(b) -> BookingResponse:
    return BookingResponse(
        id=b.id,
        customer_id=b.customer_id,
        helper_id=b.helper_id,
        quote_id=b.quote_id,
        status=b.status,
        scheduled_start=b.scheduled_start,
        scheduled_end=b.scheduled_end,
        address_snapshot=b.address_snapshot or {},
        reassignment_reason_code=b.reassignment_reason_code,
        cancellation_reason_code=b.cancellation_reason_code,
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


@router.get("/bookings", response_model=SuccessResponse[List[BookingResponse]])  # type: ignore[misc]
async def list_bookings(
    status: Optional[str] = Query(default=None),
    customer_id: Optional[str] = Query(default=None),
    helper_id: Optional[str] = Query(default=None),
    scheduled_from: Optional[datetime] = Query(default=None),
    scheduled_to: Optional[datetime] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("bookings:read:all")),
) -> SuccessResponse[List[BookingResponse]]:
    payload = AdminBookingFilterRequest(
        status=status,
        customer_id=customer_id,
        helper_id=helper_id,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        skip=skip,
        limit=limit,
    )
    bookings = await booking_operations_service.list_bookings(db, payload)
    return ResponseBuilder.success("Bookings retrieved", [_to_response(b) for b in bookings])


@router.get("/bookings/{booking_id}", response_model=SuccessResponse[BookingResponse])  # type: ignore[misc]
async def get_booking_detail(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("bookings:read:all")),
) -> SuccessResponse[BookingResponse]:
    booking = await booking_operations_service.get_booking(db, booking_id)
    return ResponseBuilder.success("Booking retrieved", _to_response(booking))


@router.post("/bookings/{booking_id}/assign", response_model=SuccessResponse[BookingResponse])  # type: ignore[misc]
async def assign_booking(
    booking_id: str,
    payload: AdminAssignBookingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings:assign")),
) -> SuccessResponse[BookingResponse]:
    booking = await booking_operations_service.assign_booking(db, current_user, booking_id, payload.helper_id)
    return ResponseBuilder.updated("Booking assigned", _to_response(booking))


@router.post("/bookings/{booking_id}/reassign", response_model=SuccessResponse[BookingResponse])  # type: ignore[misc]
async def reassign_booking(
    booking_id: str,
    payload: AdminReassignBookingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings:assign")),
) -> SuccessResponse[BookingResponse]:
    booking = await booking_operations_service.reassign_booking(
        db, current_user, booking_id, payload.helper_id, payload.reason_code
    )
    return ResponseBuilder.updated("Booking reassigned", _to_response(booking))


@router.post("/bookings/{booking_id}/cancel", response_model=SuccessResponse[BookingResponse])  # type: ignore[misc]
async def cancel_booking(
    booking_id: str,
    payload: AdminCancelBookingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings:assign")),
) -> SuccessResponse[BookingResponse]:
    booking = await booking_operations_service.cancel_booking(db, current_user, booking_id, payload.reason_code)
    return ResponseBuilder.updated("Booking cancelled", _to_response(booking))
