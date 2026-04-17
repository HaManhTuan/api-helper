from datetime import datetime
from typing import Optional

from app.schemas.common.base_schema import BaseSchema


class CustomerProfileResponse(BaseSchema):
    user_id: str
    full_name: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SavedAddressResponse(BaseSchema):
    id: str
    customer_id: str
    label: str
    line: str
    district: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime
