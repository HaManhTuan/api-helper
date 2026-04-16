from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base_model import BaseModel


class BookingFinancialSnapshot(BaseModel):
    """
    Financial breakdown snapshot for reporting/settlement.
    This is created when a booking completes (or via admin compute API for now).
    """

    booking_id = Column(String(64), nullable=False, unique=True, index=True)

    currency = Column(String(10), nullable=False, default="VND")
    customer_total = Column(Integer, nullable=False)
    subtotal_before_tax = Column(Integer, nullable=False, default=0)
    tax_total = Column(Integer, nullable=False, default=0)
    helper_total = Column(Integer, nullable=False)
    platform_total = Column(Integer, nullable=False)

    applied_price_entry_id = Column(String, ForeignKey("pricebookentrys.id"), nullable=True)
    applied_commission_rule_id = Column(String, ForeignKey("commissionrules.id"), nullable=True)

    line_items = Column(JSONB, nullable=False, default=list)
    computed_at = Column(DateTime, nullable=False, index=True)

