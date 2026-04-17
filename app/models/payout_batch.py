from sqlalchemy import Column, DateTime, Integer, String, Text

from app.models.base_model import BaseModel


class PayoutBatch(BaseModel):
    """
    Aggregated payout run for a settlement period.
    """

    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    status = Column(String(30), nullable=False, default="pending_approval", index=True)
    currency = Column(String(10), nullable=False, default="VND")
    total_lines = Column(Integer, nullable=False, default=0)
    total_amount = Column(Integer, nullable=False, default=0)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    paid_by = Column(String, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)
