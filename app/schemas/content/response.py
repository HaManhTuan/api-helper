from datetime import datetime

from app.schemas.common.base_schema import BaseSchema


class ContentBlockResponse(BaseSchema):
    id: str
    key: str
    locale: str
    title: str | None = None
    body: str
    content_format: str
    version: str
    status: str
    published_at: datetime | None = None
    published_by: str | None = None
    created_at: datetime
    updated_at: datetime
