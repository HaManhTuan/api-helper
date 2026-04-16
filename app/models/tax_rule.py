from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class TaxRule(BaseModel):
    """
    Effective-dated VAT and display rules. service_offering_id NULL = global default.
    """

    service_offering_id = Column(String, ForeignKey("serviceofferings.id"), nullable=True, index=True)

    vat_rate = Column(Numeric(5, 2), nullable=False, default=0)  # percent
    price_display_mode = Column(String(20), nullable=False, default="inclusive")  # inclusive | exclusive
    commission_base = Column(String(20), nullable=False, default="before_vat")  # before_vat | after_vat

    rounding_mode = Column(String(20), nullable=False, default="half_up")  # half_up (VND integer)

    effective_from = Column(DateTime, nullable=False, index=True)
    effective_to = Column(DateTime, nullable=True, index=True)
    priority = Column(Integer, nullable=False, default=0, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)

    service_offering = relationship("ServiceOffering")

