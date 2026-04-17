from typing import Optional

from pydantic import Field

from app.schemas.common.base_schema import BaseSchema


class CustomerProfileUpdateRequest(BaseSchema):
    full_name: Optional[str] = Field(default=None, max_length=120)
    contact_phone: Optional[str] = Field(default=None, min_length=8, max_length=20)


class SavedAddressCreateRequest(BaseSchema):
    label: str = Field(..., min_length=1, max_length=40)
    line: str = Field(..., min_length=1, max_length=500)
    district: str = Field(..., min_length=1, max_length=80)
    city: str = Field(default="Hanoi", min_length=2, max_length=80)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False


class SavedAddressUpdateRequest(BaseSchema):
    label: Optional[str] = Field(default=None, min_length=1, max_length=40)
    line: Optional[str] = Field(default=None, min_length=1, max_length=500)
    district: Optional[str] = Field(default=None, min_length=1, max_length=80)
    city: Optional[str] = Field(default=None, min_length=2, max_length=80)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: Optional[bool] = None
