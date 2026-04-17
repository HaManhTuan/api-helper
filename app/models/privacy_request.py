from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base_model import BaseModel


class PrivacyRequest(BaseModel):
    """
    DSAR workflow entity for customer privacy requests.
    """

    customer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    request_type = Column(String(20), nullable=False)
    status = Column(String(30), nullable=False, default="submitted", index=True)
    legal_basis = Column(String(80), nullable=True)
    requested_payload = Column(JSONB, nullable=True)
    resolution_summary = Column(Text, nullable=True)
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    completed_by = Column(String, ForeignKey("users.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    export_job_id = Column(String, nullable=True)
