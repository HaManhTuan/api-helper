from sqlalchemy import Boolean, Column, DateTime, String, Text

from app.models.base_model import BaseModel


class InsuranceProduct(BaseModel):
    """
    Insurance product/tier configuration.
    """

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    coverage_summary = Column(Text, nullable=False)
    premium_model = Column(String(40), nullable=False)  # fixed_monthly/per_job/included_platform_fee
    eligibility_rule = Column(String(80), nullable=False, default="approved_helpers_only")
    active = Column(Boolean, nullable=False, default=True, index=True)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
