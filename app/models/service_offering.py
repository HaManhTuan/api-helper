from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class ServiceOffering(BaseModel):
    """
    Commercial catalog root entity for cleaning services / add-ons.
    """

    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String(50), nullable=False, default="hour")  # e.g. hour, m2, package
    active = Column(Boolean, nullable=False, default=True, index=True)

    tags = Column(JSONB, nullable=False, default=list)
    meta = Column("metadata", JSONB, nullable=False, default=dict)

    price_book_entries = relationship("PriceBookEntry", back_populates="service_offering", cascade="all, delete-orphan")
    commission_rules = relationship("CommissionRule", back_populates="service_offering", cascade="all, delete-orphan")
    promotions = relationship("Promotion", back_populates="service_offering")

