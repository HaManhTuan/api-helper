from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from app.models.base_model import BaseModel


class InsuranceEnrollment(BaseModel):
    """
    Helper enrollment state per insurance product.
    """

    helper_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("insuranceproducts.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="not_enrolled", index=True)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
