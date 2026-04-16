from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class CommissionRule(BaseModel):
    """
    Effective-dated commission split configuration.
    """

    service_offering_id = Column(String, ForeignKey("serviceofferings.id"), nullable=True, index=True)

    helper_percent = Column(Numeric(5, 2), nullable=False, default=0)
    platform_percent = Column(Numeric(5, 2), nullable=False, default=0)

    fixed_platform_fee = Column(Integer, nullable=False, default=0)  # VND integer
    fixed_helper_fee = Column(Integer, nullable=False, default=0)  # VND integer

    effective_from = Column(DateTime, nullable=False, index=True)
    effective_to = Column(DateTime, nullable=True, index=True)
    priority = Column(Integer, nullable=False, default=0, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)

    service_offering = relationship("ServiceOffering", back_populates="commission_rules")

