from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base_model import BaseModel


class ReportExportJob(BaseModel):
    """
    Export job metadata for asynchronous analytics exports.
    """

    report_type = Column(String(40), nullable=False, index=True)
    filters = Column(JSONB, nullable=False, default=dict)
    status = Column(String(20), nullable=False, default="queued", index=True)  # queued/running/completed/failed
    file_ref = Column(Text, nullable=True)
    checksum = Column(String(128), nullable=True)
    error_message = Column(Text, nullable=True)
    requested_by = Column(String, ForeignKey("users.id"), nullable=False)
    completed_at = Column(DateTime, nullable=True)
