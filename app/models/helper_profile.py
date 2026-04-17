from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class HelperProfile(BaseModel):
    """
    Moderation profile and eligibility state for helper accounts.
    """

    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    display_name = Column(String(120), nullable=False)
    skills = Column(JSONB, nullable=True)
    service_area = Column(JSONB, nullable=False, default=dict)
    approval_status = Column(String(20), nullable=False, default="pending", index=True)
    suspension_reason_code = Column(String(64), nullable=True)
    aggregate_rating = Column(Numeric(3, 2), nullable=False, default=0)
    ratings_count = Column(Integer, nullable=False, default=0)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="helper_profile")
