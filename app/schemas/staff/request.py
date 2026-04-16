from typing import Optional

from pydantic import EmailStr, Field, model_validator

from app.schemas.common.base_schema import BaseSchema


class StaffCreateRequest(BaseSchema):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=8, max_length=20)
    password: str = Field(..., min_length=8)
    role_code: str = Field(..., min_length=2, max_length=50)
    status: str = Field(default="active", min_length=3, max_length=20)

    @model_validator(mode="after")
    def validate_identifier(self) -> "StaffCreateRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        return self


class StaffStatusUpdateRequest(BaseSchema):
    status: str = Field(..., min_length=3, max_length=20)


class StaffRoleUpdateRequest(BaseSchema):
    role_code: str = Field(..., min_length=2, max_length=50)


