from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class HelperDocument(BaseModel):
    """
    Helper KYC document metadata and review lifecycle.
    """

    helper_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    document_type = Column(String(50), nullable=False, index=True)
    storage_ref = Column(Text, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    status = Column(String(30), nullable=False, default="pending_review", index=True)
    review_reason_code = Column(String(64), nullable=True)
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    helper = relationship("User", foreign_keys=[helper_id], back_populates="helper_documents")
