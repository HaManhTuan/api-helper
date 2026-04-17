from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.customer_privacy import CustomerPrivacyRequestCreateRequest, CustomerPrivacyRequestResponse
from app.services.customer_privacy_service import customer_privacy_service
from app.utils.auth import get_current_customer_user

router = APIRouter()


def _to_response(item) -> CustomerPrivacyRequestResponse:
    return CustomerPrivacyRequestResponse(
        id=item.id,
        request_type=item.request_type,
        status=item.status,
        legal_basis=item.legal_basis,
        requested_payload=item.requested_payload,
        resolution_summary=item.resolution_summary,
        created_at=item.created_at,
        updated_at=item.updated_at,
        download_url=customer_privacy_service.build_download_url(item),
    )


@router.post("/customer/privacy-requests", response_model=SuccessResponse[CustomerPrivacyRequestResponse])  # type: ignore[misc]
async def create_privacy_request(
    payload: CustomerPrivacyRequestCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[CustomerPrivacyRequestResponse]:
    req = await customer_privacy_service.create_request(db, current_user, payload)
    return ResponseBuilder.created("Privacy request submitted", _to_response(req))


@router.get("/customer/privacy-requests", response_model=SuccessResponse[List[CustomerPrivacyRequestResponse]])  # type: ignore[misc]
async def list_privacy_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[List[CustomerPrivacyRequestResponse]]:
    rows = await customer_privacy_service.list_own_requests(db, current_user)
    return ResponseBuilder.success("Privacy requests retrieved", [_to_response(item) for item in rows])


@router.get("/customer/privacy-requests/{request_id}", response_model=SuccessResponse[CustomerPrivacyRequestResponse])  # type: ignore[misc]
async def get_privacy_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[CustomerPrivacyRequestResponse]:
    row = await customer_privacy_service.get_own_request(db, current_user, request_id)
    return ResponseBuilder.success("Privacy request retrieved", _to_response(row))
