from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base_model import BaseModel


class CustomerQuote(BaseModel):
    """
    Customer-facing quote snapshot before booking confirmation.
    """

    customer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    quote_code = Column(String(64), nullable=False, unique=True, index=True)
    currency = Column(String(10), nullable=False, default="VND")
    promotion_code = Column(String(64), nullable=True)
    surge_multiplier = Column(String(20), nullable=False, default="1.0")
    line_items = Column(JSONB, nullable=False, default=list)
    address_snapshot = Column(JSONB, nullable=False, default=dict)
    scheduled_start = Column(DateTime, nullable=False)
    subtotal_before_tax = Column(Integer, nullable=False, default=0)
    tax_total = Column(Integer, nullable=False, default=0)
    promotion_total = Column(Integer, nullable=False, default=0)
    customer_total = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime, nullable=False, index=True)
