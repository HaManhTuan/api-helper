from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class Role(BaseModel):
    """Internal staff role with permission matrix binding."""

    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_system = Column(String(5), nullable=False, default="false")

    users = relationship("User", back_populates="staff_role")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

