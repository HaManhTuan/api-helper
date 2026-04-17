from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base_model import BaseModel


class Booking(BaseModel):
    """
    Core booking lifecycle with assignment and operational metadata.
    """

    customer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    helper_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    quote_id = Column(String(64), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    scheduled_start = Column(DateTime, nullable=False, index=True)
    scheduled_end = Column(DateTime, nullable=True)
    address_snapshot = Column(JSONB, nullable=False, default=dict)
    reassignment_reason_code = Column(String(64), nullable=True)
    cancellation_reason_code = Column(String(64), nullable=True)
