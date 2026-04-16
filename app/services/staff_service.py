from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User
from app.schemas.staff import StaffCreateRequest, StaffRoleUpdateRequest, StaffStatusUpdateRequest
from app.schemas.users import UserCreate
from app.services.user_service import user_service


class StaffService:
    """Service layer for admin staff/role management."""

    async def create_staff(self, db: AsyncSession, actor_user: User, request: StaffCreateRequest) -> User:
        role = await self._get_role_by_code(db, request.role_code)
        user_data = UserCreate(
            role="staff",
            email=request.email,
            phone=request.phone,
            password=request.password,
            status=request.status,
        )
        staff_user = await user_service.create_user(db=db, user_data=user_data)
        staff_user.staff_role_id = role.id
        db.add(staff_user)
        await db.flush()
        await self._audit(db, actor_user.id, staff_user.id, "staff:create", f"role={role.code},status={request.status}")
        await db.commit()
        await db.refresh(staff_user)
        return staff_user

    async def list_staff(self, db: AsyncSession) -> List[User]:
        return await user_service.repository.list_internal_staff(db)

    async def update_staff_status(
        self, db: AsyncSession, actor_user: User, staff_user_id: str, request: StaffStatusUpdateRequest
    ) -> User:
        staff_user = await self._get_staff_user(db, staff_user_id)
        staff_user.status = request.status
        db.add(staff_user)
        await self._audit(db, actor_user.id, staff_user.id, "staff:status:update", f"status={request.status}")
        await db.commit()
        await db.refresh(staff_user)
        return staff_user

    async def update_staff_role(
        self, db: AsyncSession, actor_user: User, staff_user_id: str, request: StaffRoleUpdateRequest
    ) -> User:
        staff_user = await self._get_staff_user(db, staff_user_id)
        role = await self._get_role_by_code(db, request.role_code)
        staff_user.staff_role_id = role.id
        db.add(staff_user)
        await self._audit(db, actor_user.id, staff_user.id, "staff:role:update", f"role={role.code}")
        await db.commit()
        await db.refresh(staff_user)
        return staff_user

    async def list_roles(self, db: AsyncSession) -> List[Role]:
        result = await db.execute(select(Role).where(Role.deleted_at.is_(None)))
        return list(result.scalars().all())

    async def get_role_permission_codes(self, db: AsyncSession, role_id: str) -> List[str]:
        stmt = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id, Permission.deleted_at.is_(None), RolePermission.deleted_at.is_(None))
        )
        result = await db.execute(stmt)
        return [code for code in result.scalars().all()]

    async def _get_staff_user(self, db: AsyncSession, user_id: str) -> User:
        user = await user_service.get_by_id(db=db, id=user_id)
        if user is None or user.role not in {"staff", "admin"}:
            raise NotFoundException("Staff user not found")
        return user

    async def _get_role_by_code(self, db: AsyncSession, role_code: str) -> Role:
        result = await db.execute(select(Role).where(Role.code == role_code, Role.deleted_at.is_(None)))
        role = result.scalar_one_or_none()
        if role is None:
            raise NotFoundException("Role not found")
        return role

    async def _audit(self, db: AsyncSession, actor_user_id: str, target_user_id: str, action: str, details: str) -> None:
        db.add(
            StaffAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action=action,
                details=details,
            )
        )

staff_service = StaffService()

