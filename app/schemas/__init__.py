"""
Schemas package.

This package provides organized access to all application schemas.
"""

# Common schemas
from .common import (
    BaseSchema,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    ResponseBuilder,
    SuccessResponse,
)

# User schemas
from .users import (  # Internal schemas; Request/Response schemas; Converters
    UserBase,
    UserCreate,
    UserCreateRequest,
    UserInDB,
    UserProfileResponse,
    UserRegistrationRequest,
    UserResponse,
    UserUpdate,
    UserUpdateRequest,
    convert_user_create_request_to_internal,
    convert_user_registration_to_internal,
    convert_user_update_request_to_internal,
)

# Pricing/Catalog schemas
from .pricing import (  # Catalog/pricing/commission snapshots
    BookingFinancialSnapshotResponse,
    BookingLineItemBreakdownResponse,
    BookingSnapshotComputeRequest,
    CommissionRuleResponse,
    CommissionRuleUpsertRequest,
    PriceBookEntryResponse,
    PriceBookEntryUpsertRequest,
    ServiceOfferingCreateRequest,
    ServiceOfferingResponse,
    ServiceOfferingUpdateRequest,
)

# Tax/VAT schemas
from .tax import TaxConfigResponse, TaxConfigUpsertRequest, TaxRuleResponse, TaxRuleUpsertRequest

__all__ = [
    # Common
    "BaseSchema",
    "ErrorDetail",
    "ErrorResponse",
    "SuccessResponse",
    "PaginationMeta",
    "PaginatedResponse",
    "ResponseBuilder",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserRegistrationRequest",
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserResponse",
    "UserProfileResponse",
    "convert_user_registration_to_internal",
    "convert_user_create_request_to_internal",
    "convert_user_update_request_to_internal",
    # Pricing/Catalog
    "ServiceOfferingCreateRequest",
    "ServiceOfferingUpdateRequest",
    "ServiceOfferingResponse",
    "PriceBookEntryUpsertRequest",
    "PriceBookEntryResponse",
    "CommissionRuleUpsertRequest",
    "CommissionRuleResponse",
    "BookingSnapshotComputeRequest",
    "BookingFinancialSnapshotResponse",
    "BookingLineItemBreakdownResponse",
    # Tax/VAT
    "TaxRuleUpsertRequest",
    "TaxRuleResponse",
    "TaxConfigUpsertRequest",
    "TaxConfigResponse",
]
