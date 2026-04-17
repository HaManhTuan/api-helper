from sqlalchemy import Column, DateTime, String, Text

from app.models.base_model import BaseModel


class ContentBlock(BaseModel):
    """
    Versioned content block for policy/FAQ pages.
    """

    key = Column(String(80), nullable=False, index=True)
    locale = Column(String(10), nullable=False, default="vi", index=True)
    title = Column(String(200), nullable=True)
    body = Column(Text, nullable=False)
    content_format = Column(String(20), nullable=False, default="markdown")
    version = Column(String(40), nullable=False, default="v1")
    status = Column(String(20), nullable=False, default="draft", index=True)  # draft/published/archived
    published_at = Column(DateTime, nullable=True)
    published_by = Column(String, nullable=True)
