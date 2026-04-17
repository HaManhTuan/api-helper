from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.models.base_model import BaseModel


class Review(BaseModel):
    """
    Customer review for completed booking/helper.
    """

    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False, index=True)
    helper_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    customer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1..5
    comment = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="visible", index=True)  # visible/hidden/flagged
    flagged_reason_code = Column(String(64), nullable=True)
    moderated_by = Column(String, ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime, nullable=True)
