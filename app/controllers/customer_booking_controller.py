from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.bookings import BookingResponse
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.customer_booking import (
    CustomerBookingCancelRequest,
    CustomerBookingCreateRequest,
    CustomerBookingDetailResponse,
    CustomerQuoteRequest,
    CustomerQuoteResponse,
)
from app.schemas.pricing import BookingLineItemBreakdownResponse
from app.services.customer_booking_service import customer_booking_service
from app.utils.auth import get_current_customer_user

router = APIRouter()


def _booking_response(booking) -> BookingResponse:
    return BookingResponse(
        id=booking.id,
        customer_id=booking.customer_id,
        helper_id=booking.helper_id,
        quote_id=booking.quote_id,
        status=booking.status,
        scheduled_start=booking.scheduled_start,
        scheduled_end=booking.scheduled_end,
        address_snapshot=booking.address_snapshot or {},
        reassignment_reason_code=booking.reassignment_reason_code,
        cancellation_reason_code=booking.cancellation_reason_code,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


def _snapshot_to_dict(snapshot) -> dict[str, Any]:
    return {
        "id": snapshot.id,
        "currency": snapshot.currency,
        "customer_total": int(snapshot.customer_total),
        "subtotal_before_tax": int(snapshot.subtotal_before_tax),
        "tax_total": int(snapshot.tax_total),
        "promotion_total": int(snapshot.promotion_total),
        "helper_total": int(snapshot.helper_total),
        "platform_total": int(snapshot.platform_total),
        "line_items": snapshot.line_items,
        "computed_at": snapshot.computed_at.isoformat(),
    }


@router.post("/customer/bookings/quote", response_model=SuccessResponse[CustomerQuoteResponse])  # type: ignore[misc]
async def request_quote(
    payload: CustomerQuoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[CustomerQuoteResponse]:
    quote, snapshot = await customer_booking_service.request_quote(db, current_user, payload)
    return ResponseBuilder.created(
        "Quote created",
        CustomerQuoteResponse(
            quote_id=quote.quote_code,
            currency=quote.currency,
            subtotal_before_tax=int(quote.subtotal_before_tax),
            tax_total=int(quote.tax_total),
            promotion_total=int(quote.promotion_total),
            customer_total=int(quote.customer_total),
            line_items=[BookingLineItemBreakdownResponse(**line) for line in snapshot.line_items],
            expires_at=quote.expires_at,
        ),
    )


@router.post("/customer/bookings", response_model=SuccessResponse[CustomerBookingDetailResponse])  # type: ignore[misc]
async def create_booking(
    payload: CustomerBookingCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[CustomerBookingDetailResponse]:
    booking, snapshot = await customer_booking_service.create_booking(db, current_user, payload)
    booking_response = _booking_response(booking)
    return ResponseBuilder.created(
        "Booking created",
        CustomerBookingDetailResponse(**booking_response.model_dump(), financial_snapshot=_snapshot_to_dict(snapshot)),
    )


@router.get("/customer/bookings", response_model=SuccessResponse[list[BookingResponse]])  # type: ignore[misc]
async def list_own_bookings(
    status: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[list[BookingResponse]]:
    bookings = await customer_booking_service.list_own_bookings(db, current_user, status=status, skip=skip, limit=limit)
    return ResponseBuilder.success("Bookings retrieved", [_booking_response(item) for item in bookings])


@router.get("/customer/bookings/{booking_id}", response_model=SuccessResponse[CustomerBookingDetailResponse])  # type: ignore[misc]
async def get_booking_detail(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[CustomerBookingDetailResponse]:
    booking, snapshot = await customer_booking_service.get_own_booking(db, current_user, booking_id)
    booking_response = _booking_response(booking)
    snapshot_data = _snapshot_to_dict(snapshot) if snapshot else None
    return ResponseBuilder.success(
        "Booking retrieved",
        CustomerBookingDetailResponse(**booking_response.model_dump(), financial_snapshot=snapshot_data),
    )


@router.post("/customer/bookings/{booking_id}/cancel", response_model=SuccessResponse[BookingResponse])  # type: ignore[misc]
async def cancel_booking(
    booking_id: str,
    payload: CustomerBookingCancelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[BookingResponse]:
    booking = await customer_booking_service.cancel_own_booking(db, current_user, booking_id, payload.reason_code)
    return ResponseBuilder.updated("Booking cancelled", _booking_response(booking))
