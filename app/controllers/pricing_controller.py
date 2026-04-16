from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.pricing import (
    BookingFinancialSnapshotResponse,
    BookingSnapshotComputeRequest,
    CommissionRuleResponse,
    CommissionRuleUpsertRequest,
    PriceBookEntryResponse,
    PriceBookEntryUpsertRequest,
    ServiceOfferingCreateRequest,
    ServiceOfferingResponse,
    ServiceOfferingUpdateRequest,
)
from app.services.pricing_service import pricing_service
from app.utils.auth import require_permission

router = APIRouter()


def _service_to_response(o) -> ServiceOfferingResponse:
    return ServiceOfferingResponse(
        id=o.id,
        code=o.code,
        name=o.name,
        description=o.description,
        unit=o.unit,
        active=bool(o.active),
        tags=o.tags or [],
        metadata=o.meta or {},
        created_at=o.created_at,
        updated_at=o.updated_at,
    )


def _price_entry_to_response(e) -> PriceBookEntryResponse:
    return PriceBookEntryResponse(
        id=e.id,
        service_offering_id=e.service_offering_id,
        variant_code=e.variant_code,
        zone_code=e.zone_code,
        currency=e.currency,
        customer_price=int(e.customer_price),
        reference_cost=int(e.reference_cost),
        margin=int(e.customer_price) - int(e.reference_cost),
        effective_from=e.effective_from,
        effective_to=e.effective_to,
        priority=int(e.priority),
        active=bool(e.active),
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


def _commission_to_response(r) -> CommissionRuleResponse:
    return CommissionRuleResponse(
        id=r.id,
        service_offering_id=r.service_offering_id,
        helper_percent=float(r.helper_percent),
        platform_percent=float(r.platform_percent),
        fixed_platform_fee=int(r.fixed_platform_fee),
        fixed_helper_fee=int(r.fixed_helper_fee),
        effective_from=r.effective_from,
        effective_to=r.effective_to,
        priority=int(r.priority),
        active=bool(r.active),
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.post("/catalog/services", response_model=SuccessResponse[ServiceOfferingResponse])  # type: ignore[misc]
async def create_service_offering(
    payload: ServiceOfferingCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[ServiceOfferingResponse]:
    offering = await pricing_service.create_service_offering(db=db, actor=current_user, payload=payload)
    return ResponseBuilder.created("Service offering created", _service_to_response(offering))


@router.put("/catalog/services/{offering_id}", response_model=SuccessResponse[ServiceOfferingResponse])  # type: ignore[misc]
async def update_service_offering(
    offering_id: str,
    payload: ServiceOfferingUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[ServiceOfferingResponse]:
    offering = await pricing_service.update_service_offering(db=db, actor=current_user, offering_id=offering_id, payload=payload)
    return ResponseBuilder.updated("Service offering updated", _service_to_response(offering))


@router.get("/catalog/services", response_model=SuccessResponse[List[ServiceOfferingResponse]])  # type: ignore[misc]
async def list_service_offerings(
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[List[ServiceOfferingResponse]]:
    offerings = await pricing_service.list_service_offerings(db=db, include_inactive=include_inactive)
    return ResponseBuilder.success("Service offerings retrieved", [_service_to_response(o) for o in offerings])


@router.post("/price-book/entries", response_model=SuccessResponse[PriceBookEntryResponse])  # type: ignore[misc]
async def create_price_book_entry(
    payload: PriceBookEntryUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[PriceBookEntryResponse]:
    entry = await pricing_service.upsert_price_book_entry(db=db, actor=current_user, payload=payload)
    return ResponseBuilder.created("Price book entry created", _price_entry_to_response(entry))


@router.get("/price-book/entries", response_model=SuccessResponse[List[PriceBookEntryResponse]])  # type: ignore[misc]
async def list_price_book_entries(
    service_code: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[List[PriceBookEntryResponse]]:
    entries = await pricing_service.list_price_book_entries(db=db, service_code=service_code)
    return ResponseBuilder.success("Price book entries retrieved", [_price_entry_to_response(e) for e in entries])


@router.post("/commission-rules", response_model=SuccessResponse[CommissionRuleResponse])  # type: ignore[misc]
async def create_commission_rule(
    payload: CommissionRuleUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[CommissionRuleResponse]:
    rule = await pricing_service.upsert_commission_rule(db=db, actor=current_user, payload=payload)
    return ResponseBuilder.created("Commission rule created", _commission_to_response(rule))


@router.get("/commission-rules", response_model=SuccessResponse[List[CommissionRuleResponse]])  # type: ignore[misc]
async def list_commission_rules(
    service_code: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[List[CommissionRuleResponse]]:
    rules = await pricing_service.list_commission_rules(db=db, service_code=service_code)
    return ResponseBuilder.success("Commission rules retrieved", [_commission_to_response(r) for r in rules])


@router.post("/snapshots/compute", response_model=SuccessResponse[BookingFinancialSnapshotResponse])  # type: ignore[misc]
async def compute_booking_snapshot(
    payload: BookingSnapshotComputeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[BookingFinancialSnapshotResponse]:
    snap = await pricing_service.compute_and_persist_snapshot(db=db, actor=current_user, payload=payload)
    return ResponseBuilder.created(
        "Booking financial snapshot computed",
        BookingFinancialSnapshotResponse(
            id=snap.id,
            booking_id=snap.booking_id,
            currency=snap.currency,
            customer_total=int(snap.customer_total),
            helper_total=int(snap.helper_total),
            platform_total=int(snap.platform_total),
            line_items=snap.line_items,  # type: ignore[arg-type]
            computed_at=snap.computed_at,
        ),
    )

