from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException
from app.models.user import User
from app.repositories.concrete.user_repository import UserRepository, user_repository
from app.schemas.users import UserCreate
from app.services.base_service import BaseService
from app.utils.i18n import __
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("user-service")


class UserService(BaseService[User, UserRepository]):
    """Service for user-related operations"""

    def __init__(self) -> None:
        super().__init__(user_repository)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        logger.debug(f"Looking up user by email: {email}")
        return await user_repository.get_by_email(db, email=email)

    async def get_by_phone(self, db: AsyncSession, phone: str) -> Optional[User]:
        """Get user by phone"""
        logger.debug(f"Looking up user by phone: {phone}")
        return await user_repository.get_by_phone(db, phone=phone)

    async def get_by_identifier(self, db: AsyncSession, identifier: str) -> Optional[User]:
        """Get user by login identifier (email or phone)."""
        logger.debug(f"Looking up user by identifier: {identifier}")
        return await user_repository.get_by_identifier(db, identifier=identifier)

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Backward-compatible alias for identifier lookup."""
        return await self.get_by_identifier(db=db, identifier=username)

    async def create_user(
        self,
        db: AsyncSession,
        user_data: UserCreate,
    ) -> User:
        """Create a new user"""
        logger.info(f"Creating new user with email: {user_data.email}, phone: {user_data.phone}")

        if not user_data.email and not user_data.phone:
            raise ConflictException(__("auth.login_failed"))

        # Check if email already exists
        if await self.get_by_email(db, email=user_data.email):
            logger.warning(f"Attempt to create user with existing email: {user_data.email}")
            raise ConflictException(__("user.email_already_exists"))

        # Check if phone already exists
        if user_data.phone and await self.get_by_phone(db, phone=user_data.phone):
            logger.warning(f"Attempt to create user with existing phone: {user_data.phone}")
            raise ConflictException(__("user.email_already_exists"))

        # Create user using the schema
        return await user_repository.create(db, obj_in=user_data)

    async def authenticate_user(self, db: AsyncSession, identifier: str, password: str) -> Optional[User]:
        """Authenticate a user by email/phone identifier and password."""
        if not identifier:
            return None
        logger.debug(f"Authenticating user: {identifier}")
        user = await self.get_by_identifier(db, identifier=identifier)

        if not user:
            logger.warning(f"Authentication failed: user not found: {identifier}")
            return None

        if not user.check_password(password):
            logger.warning(f"Authentication failed: incorrect password for user: {identifier}")
            return None

        return user

    async def update_user_with_optimistic_lock(
        self,
        db: AsyncSession,
        user_id: str,
        update_data: dict,
        expected_updated_at: Optional[str] = None,
    ) -> User:
        """Update user with optimistic locking"""
        logger.debug(f"Updating user {user_id} with optimistic lock")
        return await user_repository.update_with_optimistic_lock(
            db=db,
            id=user_id,
            obj_in=update_data,
            expected_updated_at=expected_updated_at,
        )

    async def get_effective_permissions(self, db: AsyncSession, user: User) -> List[str]:
        """
        Resolve permissions for internal users from source of truth.
        """
        if user.role == "admin":
            return ["*"]
        if user.role != "staff":
            return []
        return await user_repository.get_permission_codes(db=db, user_id=user.id)


# Create instance for dependency injection
user_service = UserService()
