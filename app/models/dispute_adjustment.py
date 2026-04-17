from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.models.base_model import BaseModel


class DisputeAdjustment(BaseModel):
    """
    Financial adjustment entries resulting from dispute handling.
    """

    dispute_id = Column(String, ForeignKey("disputes.id"), nullable=False, index=True)
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False, index=True)
    direction = Column(String(20), nullable=False)
    target_party = Column(String(20), nullable=False)
    amount = Column(Integer, nullable=False)  # VND integer
    reason_code = Column(String(64), nullable=False)
    note = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
