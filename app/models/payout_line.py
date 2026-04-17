from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base_model import BaseModel


class PayoutLine(BaseModel):
    """
    Helper-level payout line item inside a payout batch.
    """

    payout_batch_id = Column(String, ForeignKey("payoutbatchs.id"), nullable=False, index=True)
    helper_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    currency = Column(String(10), nullable=False, default="VND")
    base_amount = Column(Integer, nullable=False, default=0)
    adjustment_amount = Column(Integer, nullable=False, default=0)
    total_amount = Column(Integer, nullable=False, default=0)
    booking_ids = Column(JSONB, nullable=False, default=list)
    booking_count = Column(Integer, nullable=False, default=0)
