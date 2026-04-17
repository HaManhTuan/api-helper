from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class PromotionRedemption(BaseModel):
    """
    Promotion usage log for analytics and limits.
    """

    promotion_id = Column(String, ForeignKey("promotions.id"), nullable=False, index=True)
    customer_id = Column(String, nullable=False, index=True)
    booking_id = Column(String, nullable=True, index=True)
    quote_id = Column(String, nullable=True, index=True)

    redeemed_amount = Column(Integer, nullable=False, default=0)  # VND integer
    currency = Column(String(3), nullable=False, default="VND")
    status = Column(String(20), nullable=False, default="consumed")  # reserved/consumed/released/expired
    redeemed_at = Column(DateTime, nullable=False)
    consumed_at = Column(DateTime, nullable=True)

    promotion = relationship("Promotion", back_populates="redemptions")
