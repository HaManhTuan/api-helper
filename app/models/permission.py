from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class Permission(BaseModel):
    """Permission unit for staff authorization matrix."""

    code = Column(String(100), nullable=False, unique=True, index=True)
    resource = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

