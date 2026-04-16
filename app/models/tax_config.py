from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base_model import BaseModel


class TaxConfig(BaseModel):
    """
    Singleton-like configuration for VAT and display behavior.
    """

    key = Column(String(50), nullable=False, unique=True, index=True)
    value = Column(JSONB, nullable=False, default=dict)

