from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base_model import BaseModel


class PrivacyRequestEvent(BaseModel):
    """
    Append-only event timeline for privacy request state changes.
    """

    privacy_request_id = Column(String, ForeignKey("privacyrequests.id"), nullable=False, index=True)
    event_type = Column(String(40), nullable=False)
    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=True)
    actor_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    metadata_json = Column("metadata", JSONB, nullable=True)
