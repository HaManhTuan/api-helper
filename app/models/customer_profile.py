from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base_model import BaseModel


class CustomerProfile(BaseModel):
    """
    Customer profile extension for display/contact preferences.
    """

    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    full_name = Column(String(120), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    preferences = Column(JSONB, nullable=False, default=dict)
