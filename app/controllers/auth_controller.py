from datetime import timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.settings import settings
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.users import (
    UserLoginRequest,
    UserProfileResponse,
    UserRegistrationRequest,
    UserUpdateRequest,
    convert_user_registration_to_internal,
    convert_user_update_request_to_internal,
)
from app.services.user_service import user_service
from app.utils.auth import create_access_token, get_current_admin_user, get_current_user
from app.utils.i18n import __
from app.utils.tracing import get_trace_logger

# Public router for authentication endpoints that don't require auth
public_router = APIRouter()
# Protected router for endpoints that require authentication
protected_router = APIRouter()

logger = get_trace_logger("auth-controller")


async def _build_auth_claims(user: User, db: AsyncSession) -> Dict[str, object]:
    """
    Build JWT claims aligned with FR-045.
    """
    roles = [user.role]
    permissions = await user_service.get_effective_permissions(db=db, user=user)
    return {
        "sub": user.identifier,
        "roles": roles,
        "permissions": permissions,
    }


@public_router.post("/token")  # type: ignore[misc]
async def login_for_access_token(
    login_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[Dict[str, str]]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # The logger already has the request ID from our middleware

    # Authenticate user
    user = await user_service.authenticate_user(db=db, identifier=login_data.identifier, password=login_data.password)

    if not user:
        logger.warning(f"Failed login attempt for identifier: {login_data.identifier}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=__("auth.login_failed"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {login_data.identifier}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=__("auth.login_inactive_user"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data=await _build_auth_claims(user, db), expires_delta=access_token_expires)

    logger.info(f"User {login_data.identifier} logged in successfully")

    return ResponseBuilder.success(
        message=__("auth.login_success"), data={"access_token": access_token, "token_type": "bearer"}
    )


@public_router.post("/register", response_model=SuccessResponse[Dict[str, str]])  # type: ignore[misc]
async def register(
    user_data: UserRegistrationRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[Dict[str, str]]:
    """
    Register a new user
    """
    logger.info(f"User registration attempt: email={user_data.email}, phone={user_data.phone}, role={user_data.role}")

    # Public signup only allows customer/helper accounts.
    if user_data.role not in {"customer", "helper"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration does not allow this role",
        )

    # Convert request schema to internal schema
    internal_user_data = convert_user_registration_to_internal(user_data)

    # Create user
    user = await user_service.create_user(
        db=db,
        user_data=internal_user_data,
    )

    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data=await _build_auth_claims(user, db), expires_delta=access_token_expires)

    logger.info(f"User registered successfully: {user.identifier}")

    return ResponseBuilder.success(
        message=__("auth.register_success"), data={"access_token": access_token, "token_type": "bearer"}
    )


@protected_router.get("/profile", response_model=SuccessResponse[UserProfileResponse])  # type: ignore[misc]
async def get_user_profile(
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[UserProfileResponse]:
    """
    Get current user profile
    """
    logger.info(f"User {current_user.identifier} requested profile")

    user_profile = UserProfileResponse(
        id=current_user.id,
        role=current_user.role,
        email=current_user.email,
        phone=current_user.phone,
        status=current_user.status,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        deleted_at=current_user.deleted_at,
    )

    return ResponseBuilder.success(message=__("auth.profile_retrieved"), data=user_profile)


@protected_router.put("/profile", response_model=SuccessResponse[UserProfileResponse])  # type: ignore[misc]
async def update_user_profile(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[UserProfileResponse]:
    """
    Update user profile with optimistic locking
    """
    logger.info(f"User {current_user.identifier} updating profile")

    # Convert request schema to internal schema
    internal_update_data = convert_user_update_request_to_internal(user_update)

    # Use optimistic locking for the update
    updated_user = await user_service.update_user_with_optimistic_lock(
        db=db,
        user_id=current_user.id,
        update_data=internal_update_data.dict(exclude_unset=True),
        expected_updated_at=internal_update_data.updated_at,
    )

    logger.info(f"User {current_user.identifier} profile updated successfully")

    user_profile = UserProfileResponse(
        id=updated_user.id,
        role=updated_user.role,
        email=updated_user.email,
        phone=updated_user.phone,
        status=updated_user.status,
        last_login_at=updated_user.last_login_at,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        deleted_at=updated_user.deleted_at,
    )

    return ResponseBuilder.success(
        message=__("auth.profile_updated"),
        data=user_profile,
    )


@protected_router.get("/admin/me", response_model=SuccessResponse[UserProfileResponse])  # type: ignore[misc]
async def get_admin_profile(
    current_user: User = Depends(get_current_admin_user),
) -> SuccessResponse[UserProfileResponse]:
    """
    Validate admin access and return current admin profile.
    """
    user_profile = UserProfileResponse(
        id=current_user.id,
        role=current_user.role,
        email=current_user.email,
        phone=current_user.phone,
        status=current_user.status,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        deleted_at=current_user.deleted_at,
    )
    return ResponseBuilder.success(message="Admin profile retrieved", data=user_profile)
