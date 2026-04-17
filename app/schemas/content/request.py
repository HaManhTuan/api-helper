from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class ContentBlockUpsertRequest(BaseSchema):
    key: str = Field(..., min_length=2, max_length=80)
    locale: str = Field(default="vi", min_length=2, max_length=10)
    title: str | None = Field(default=None, max_length=200)
    body: str = Field(..., min_length=1)
    content_format: str = Field(default="markdown", min_length=2, max_length=20)
    version: str = Field(default="v1", min_length=1, max_length=40)
    status: str = Field(default="draft", min_length=4, max_length=20)
