from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class RolePermission(BaseModel):
    """Join table for role to permission mapping."""

    role_id = Column(String, ForeignKey("roles.id"), nullable=False, index=True)
    permission_id = Column(String, ForeignKey("permissions.id"), nullable=False, index=True)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)

