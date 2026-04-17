from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class Promotion(BaseModel):
    """
    Promotion/voucher campaign configuration.
    """

    code = Column(String(64), nullable=False, unique=True, index=True)
    promotion_type = Column(String(20), nullable=False)  # percent/fixed
    service_id = Column(String, ForeignKey("serviceofferings.id"), nullable=True, index=True)

    discount_percent = Column(Numeric(5, 2), nullable=True)
    discount_amount = Column(Integer, nullable=True)  # VND integer

    max_redemptions = Column(Integer, nullable=True)
    per_user_limit = Column(Integer, nullable=True)
    stack_rule = Column(String(30), nullable=False, default="surge_then_promotion")

    effective_from = Column(DateTime, nullable=False, index=True)
    effective_to = Column(DateTime, nullable=True, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)

    service_offering = relationship("ServiceOffering", back_populates="promotions")
    redemptions = relationship("PromotionRedemption", back_populates="promotion")
