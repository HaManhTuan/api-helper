from sqlalchemy import Boolean, Column, Integer, String

from app.models.base_model import BaseModel


class HelperDocumentType(BaseModel):
    """
    Configurable KYC document types for helper verification.
    """

    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(120), nullable=False)
    required = Column(Boolean, nullable=False, default=False, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)
    sort_order = Column(Integer, nullable=False, default=0)
