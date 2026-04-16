from datetime import datetime
from typing import List, Optional

from app.schemas.common.base_schema import BaseSchema


class StaffUserResponse(BaseSchema):
    id: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    staff_role_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RoleResponse(BaseSchema):
    id: str
    name: str
    code: str
    description: Optional[str] = None
    permission_codes: List[str] = []

