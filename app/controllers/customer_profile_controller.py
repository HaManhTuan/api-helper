from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.customer_portal import (
    CustomerProfileResponse,
    CustomerProfileUpdateRequest,
    SavedAddressCreateRequest,
    SavedAddressResponse,
    SavedAddressUpdateRequest,
)
from app.services.customer_profile_service import customer_profile_service
from app.utils.auth import get_current_customer_user

router = APIRouter()


def _profile_response(item) -> CustomerProfileResponse:
    return CustomerProfileResponse(
        user_id=item.user_id,
        full_name=item.full_name,
        contact_phone=item.contact_phone,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _address_response(item) -> SavedAddressResponse:
    return SavedAddressResponse(
        id=item.id,
        customer_id=item.customer_id,
        label=item.label,
        line=item.line,
        district=item.district,
        city=item.city,
        latitude=float(item.latitude) if item.latitude is not None else None,
        longitude=float(item.longitude) if item.longitude is not None else None,
        is_default=bool(item.is_default),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/customer/profile", response_model=SuccessResponse[CustomerProfileResponse])  # type: ignore[misc]
async def get_customer_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[CustomerProfileResponse]:
    profile = await customer_profile_service.get_or_create_profile(db, current_user)
    return ResponseBuilder.success("Customer profile retrieved", _profile_response(profile))


@router.put("/customer/profile", response_model=SuccessResponse[CustomerProfileResponse])  # type: ignore[misc]
async def update_customer_profile(
    payload: CustomerProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[CustomerProfileResponse]:
    profile = await customer_profile_service.update_profile(db, current_user, payload)
    return ResponseBuilder.updated("Customer profile updated", _profile_response(profile))


@router.get("/customer/addresses", response_model=SuccessResponse[List[SavedAddressResponse]])  # type: ignore[misc]
async def list_saved_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[List[SavedAddressResponse]]:
    rows = await customer_profile_service.list_addresses(db, current_user)
    return ResponseBuilder.success("Saved addresses retrieved", [_address_response(item) for item in rows])


@router.post("/customer/addresses", response_model=SuccessResponse[SavedAddressResponse])  # type: ignore[misc]
async def create_saved_address(
    payload: SavedAddressCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[SavedAddressResponse]:
    row = await customer_profile_service.create_address(db, current_user, payload)
    return ResponseBuilder.created("Saved address created", _address_response(row))


@router.put("/customer/addresses/{address_id}", response_model=SuccessResponse[SavedAddressResponse])  # type: ignore[misc]
async def update_saved_address(
    address_id: str,
    payload: SavedAddressUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[SavedAddressResponse]:
    row = await customer_profile_service.update_address(db, current_user, address_id, payload)
    return ResponseBuilder.updated("Saved address updated", _address_response(row))


@router.delete("/customer/addresses/{address_id}", response_model=SuccessResponse[None])  # type: ignore[misc]
async def delete_saved_address(
    address_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer_user),
) -> SuccessResponse[None]:
    await customer_profile_service.delete_address(db, current_user, address_id)
    return ResponseBuilder.deleted("Saved address deleted")
