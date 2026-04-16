from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class PriceBookEntry(BaseModel):
    """
    Effective-dated pricing entry for a service offering.
    """

    service_offering_id = Column(String, ForeignKey("serviceofferings.id"), nullable=False, index=True)

    variant_code = Column(String(50), nullable=True, index=True)
    zone_code = Column(String(50), nullable=True, index=True)  # Hanoi district code, optional

    currency = Column(String(10), nullable=False, default="VND")
    customer_price = Column(Integer, nullable=False)  # VND integer
    reference_cost = Column(Integer, nullable=False, default=0)  # VND integer

    effective_from = Column(DateTime, nullable=False, index=True)
    effective_to = Column(DateTime, nullable=True, index=True)
    priority = Column(Integer, nullable=False, default=0, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)

    service_offering = relationship("ServiceOffering", back_populates="price_book_entries")

