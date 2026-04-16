from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.staff import (
    RoleResponse,
    StaffCreateRequest,
    StaffRoleUpdateRequest,
    StaffStatusUpdateRequest,
    StaffUserResponse,
)
from app.services.staff_service import staff_service
from app.utils.auth import require_permission

router = APIRouter()


def _to_staff_response(user: User) -> StaffUserResponse:
    return StaffUserResponse(
        id=user.id,
        role=user.role,
        email=user.email,
        phone=user.phone,
        status=user.status,
        staff_role_code=user.staff_role.code if user.staff_role else None,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/staff", response_model=SuccessResponse[StaffUserResponse])  # type: ignore[misc]
async def create_staff(
    payload: StaffCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("staff:manage")),
) -> SuccessResponse[StaffUserResponse]:
    staff_user = await staff_service.create_staff(db=db, actor_user=current_user, request=payload)
    return ResponseBuilder.created("Staff user created", _to_staff_response(staff_user))


@router.get("/staff", response_model=SuccessResponse[List[StaffUserResponse]])  # type: ignore[misc]
async def list_staff(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("staff:manage")),
) -> SuccessResponse[List[StaffUserResponse]]:
    users = await staff_service.list_staff(db=db)
    return ResponseBuilder.success("Staff users retrieved", [_to_staff_response(user) for user in users])


@router.put("/staff/{staff_user_id}/status", response_model=SuccessResponse[StaffUserResponse])  # type: ignore[misc]
async def update_staff_status(
    staff_user_id: str,
    payload: StaffStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("staff:manage")),
) -> SuccessResponse[StaffUserResponse]:
    staff_user = await staff_service.update_staff_status(
        db=db,
        actor_user=current_user,
        staff_user_id=staff_user_id,
        request=payload,
    )
    return ResponseBuilder.updated("Staff status updated", _to_staff_response(staff_user))


@router.put("/staff/{staff_user_id}/role", response_model=SuccessResponse[StaffUserResponse])  # type: ignore[misc]
async def update_staff_role(
    staff_user_id: str,
    payload: StaffRoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("staff:manage")),
) -> SuccessResponse[StaffUserResponse]:
    staff_user = await staff_service.update_staff_role(
        db=db,
        actor_user=current_user,
        staff_user_id=staff_user_id,
        request=payload,
    )
    return ResponseBuilder.updated("Staff role updated", _to_staff_response(staff_user))


@router.get("/roles", response_model=SuccessResponse[List[RoleResponse]])  # type: ignore[misc]
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("staff:manage")),
) -> SuccessResponse[List[RoleResponse]]:
    roles = await staff_service.list_roles(db=db)
    role_responses: List[RoleResponse] = []
    for role in roles:
        codes = await staff_service.get_role_permission_codes(db=db, role_id=role.id)
        role_responses.append(
            RoleResponse(
                id=role.id,
                name=role.name,
                code=role.code,
                description=role.description,
                permission_codes=codes,
            )
        )
    return ResponseBuilder.success("Roles retrieved", role_responses)

