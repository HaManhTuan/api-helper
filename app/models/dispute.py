from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from app.models.base_model import BaseModel


class Dispute(BaseModel):
    """
    Dispute case linked to booking operations and resolution workflow.
    """

    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False, index=True)
    owner_staff_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    dispute_type = Column(String(40), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="open", index=True)
    description = Column(Text, nullable=True)
    insurance_claim_id = Column(String, nullable=True, index=True)
    opened_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
