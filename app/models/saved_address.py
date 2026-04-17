from sqlalchemy import Boolean, Column, ForeignKey, Numeric, String, Text

from app.models.base_model import BaseModel


class SavedAddress(BaseModel):
    """
    Saved customer address for quick booking.
    """

    customer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    label = Column(String(40), nullable=False)
    line = Column(Text, nullable=False)
    district = Column(String(80), nullable=False)
    city = Column(String(80), nullable=False, default="Hanoi")
    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False, index=True)
