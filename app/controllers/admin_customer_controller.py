from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse, ResponseBuilder, SuccessResponse
from app.schemas.customers import (
    AdminCustomerDetailResponse,
    AdminCustomerListItemResponse,
    AdminCustomerListRequest,
    AdminCustomerStatusUpdateRequest,
    PrivacyRequestCreateRequest,
    PrivacyRequestResponse,
    PrivacyRequestReviewRequest,
)
from app.services.admin_customer_service import admin_customer_service
from app.utils.auth import require_permission

router = APIRouter()


def _customer_list_item_response(item: User) -> AdminCustomerListItemResponse:
    return AdminCustomerListItemResponse(
        id=item.id,
        email=item.email,
        phone=item.phone,
        status=item.status,
        created_at=item.created_at,
    )


def _customer_detail_response(item: User, booking_counts: dict) -> AdminCustomerDetailResponse:
    return AdminCustomerDetailResponse(
        id=item.id,
        email=item.email,
        phone=item.phone,
        status=item.status,
        created_at=item.created_at,
        updated_at=item.updated_at,
        booking_counts=booking_counts,
    )


def _privacy_response(item) -> PrivacyRequestResponse:
    return PrivacyRequestResponse(
        id=item.id,
        customer_id=item.customer_id,
        request_type=item.request_type,
        status=item.status,
        legal_basis=item.legal_basis,
        requested_payload=item.requested_payload,
        resolution_summary=item.resolution_summary,
        reviewed_by=item.reviewed_by,
        reviewed_at=item.reviewed_at,
        completed_by=item.completed_by,
        completed_at=item.completed_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/customers", response_model=PaginatedResponse[AdminCustomerListItemResponse])  # type: ignore[misc]
async def list_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("users:read")),
) -> PaginatedResponse[AdminCustomerListItemResponse]:
    payload = AdminCustomerListRequest(page=page, page_size=page_size, search=search, status=status)
    items, total = await admin_customer_service.list_customers(db, payload)
    return ResponseBuilder.paginated(
        "Customers retrieved",
        [_customer_list_item_response(item) for item in items],
        page=page,
        per_page=page_size,
        total=total,
    )


@router.get("/customers/{customer_id}", response_model=SuccessResponse[AdminCustomerDetailResponse])  # type: ignore[misc]
async def get_customer_detail(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("users:read")),
) -> SuccessResponse[AdminCustomerDetailResponse]:
    customer, booking_counts = await admin_customer_service.get_customer_detail(db, customer_id)
    return ResponseBuilder.success("Customer retrieved", _customer_detail_response(customer, booking_counts))


@router.post("/customers/{customer_id}/suspend", response_model=SuccessResponse[AdminCustomerDetailResponse])  # type: ignore[misc]
async def suspend_customer(
    customer_id: str,
    payload: AdminCustomerStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:read")),
) -> SuccessResponse[AdminCustomerDetailResponse]:
    customer = await admin_customer_service.suspend_customer(db, current_user, customer_id, payload)
    _, booking_counts = await admin_customer_service.get_customer_detail(db, customer_id)
    return ResponseBuilder.updated("Customer suspended", _customer_detail_response(customer, booking_counts))


@router.post("/customers/{customer_id}/reactivate", response_model=SuccessResponse[AdminCustomerDetailResponse])  # type: ignore[misc]
async def reactivate_customer(
    customer_id: str,
    payload: AdminCustomerStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:read")),
) -> SuccessResponse[AdminCustomerDetailResponse]:
    customer = await admin_customer_service.reactivate_customer(db, current_user, customer_id, payload)
    _, booking_counts = await admin_customer_service.get_customer_detail(db, customer_id)
    return ResponseBuilder.updated("Customer reactivated", _customer_detail_response(customer, booking_counts))


@router.post("/customers/{customer_id}/privacy-requests", response_model=SuccessResponse[PrivacyRequestResponse])  # type: ignore[misc]
async def create_privacy_request(
    customer_id: str,
    payload: PrivacyRequestCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:privacy")),
) -> SuccessResponse[PrivacyRequestResponse]:
    req = await admin_customer_service.create_privacy_request(db, current_user, customer_id, payload)
    return ResponseBuilder.created("Privacy request created", _privacy_response(req))


@router.get("/customers/{customer_id}/privacy-requests", response_model=SuccessResponse[List[PrivacyRequestResponse]])  # type: ignore[misc]
async def list_privacy_requests(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("users:privacy")),
) -> SuccessResponse[List[PrivacyRequestResponse]]:
    items = await admin_customer_service.list_privacy_requests(db, customer_id)
    return ResponseBuilder.success("Privacy requests retrieved", [_privacy_response(item) for item in items])


@router.put("/privacy-requests/{request_id}/review", response_model=SuccessResponse[PrivacyRequestResponse])  # type: ignore[misc]
async def review_privacy_request(
    request_id: str,
    payload: PrivacyRequestReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:privacy")),
) -> SuccessResponse[PrivacyRequestResponse]:
    item = await admin_customer_service.review_privacy_request(db, current_user, request_id, payload)
    return ResponseBuilder.updated("Privacy request updated", _privacy_response(item))
