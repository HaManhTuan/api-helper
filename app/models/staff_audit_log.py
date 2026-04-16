from sqlalchemy import Column, String, Text

from app.models.base_model import BaseModel


class StaffAuditLog(BaseModel):
    """Audit log for staff role/permission and status changes."""

    actor_user_id = Column(String, nullable=False, index=True)
    target_user_id = Column(String, nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    details = Column(Text, nullable=True)

