from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.models.base_model import BaseModel


class InsuranceClaim(BaseModel):
    """
    Insurance/risk claim intake linked to booking.
    """

    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False, index=True)
    reporter_role = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, default="medium")
    status = Column(String(30), nullable=False, default="opened", index=True)  # opened/under_review/accepted/rejected/closed
    resolution_notes = Column(Text, nullable=True)
    payout_amount = Column(Integer, nullable=True)
