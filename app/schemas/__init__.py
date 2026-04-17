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
from .promotions import PromotionPerformanceResponse, PromotionRedeemPreviewRequest, PromotionResponse, PromotionUpsertRequest
from .helpers import (
    HelperDocumentResponse,
    HelperDocumentReviewRequest,
    HelperDocumentSubmitRequest,
    HelperDocumentTypeResponse,
    HelperDocumentTypeUpsertRequest,
    HelperDocumentUploadIntentRequest,
    HelperDocumentUploadIntentResponse,
    HelperEligibilityResponse,
    HelperModerationActionRequest,
    HelperModerationDetailResponse,
    HelperProfileResponse,
    HelperProfileUpsertRequest,
)
from .bookings import (
    AdminAssignBookingRequest,
    AdminBookingFilterRequest,
    AdminCancelBookingRequest,
    AdminReassignBookingRequest,
    BookingResponse,
)
from .disputes import (
    DisputeAdjustmentCreateRequest,
    DisputeAdjustmentResponse,
    DisputeCreateRequest,
    DisputeResponse,
    DisputeUpdateRequest,
)
from .customers import (
    AdminCustomerDetailResponse,
    AdminCustomerListItemResponse,
    AdminCustomerListRequest,
    AdminCustomerStatusUpdateRequest,
    PrivacyRequestCreateRequest,
    PrivacyRequestResponse,
    PrivacyRequestReviewRequest,
)
from .payouts import (
    PayoutBatchDetailResponse,
    PayoutBatchGenerateRequest,
    PayoutBatchMarkPaidRequest,
    PayoutBatchResponse,
    PayoutExportResponse,
    PayoutLineResponse,
)
from .reviews import (
    HelperAggregateResponse,
    ReviewAggregateOverrideRequest,
    ReviewModerationActionRequest,
    ReviewModerationFilterRequest,
    ReviewModerationResponse,
)
from .content import ContentBlockResponse, ContentBlockUpsertRequest
from .insurance import (
    InsuranceClaimCreateRequest,
    InsuranceClaimResponse,
    InsuranceClaimUpdateRequest,
    InsuranceEnrollmentResponse,
    InsuranceEnrollmentUpsertRequest,
    InsuranceProductResponse,
    InsuranceProductUpsertRequest,
    ServiceInsuranceRuleResponse,
    ServiceInsuranceRuleUpdateRequest,
)

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
    # Promotions
    "PromotionUpsertRequest",
    "PromotionRedeemPreviewRequest",
    "PromotionResponse",
    "PromotionPerformanceResponse",
    # Helpers moderation/KYC
    "HelperDocumentTypeUpsertRequest",
    "HelperDocumentUploadIntentRequest",
    "HelperDocumentSubmitRequest",
    "HelperDocumentReviewRequest",
    "HelperModerationActionRequest",
    "HelperProfileUpsertRequest",
    "HelperProfileResponse",
    "HelperModerationDetailResponse",
    "HelperDocumentTypeResponse",
    "HelperDocumentResponse",
    "HelperDocumentUploadIntentResponse",
    "HelperEligibilityResponse",
    # Admin booking operations
    "AdminAssignBookingRequest",
    "AdminReassignBookingRequest",
    "AdminCancelBookingRequest",
    "AdminBookingFilterRequest",
    "BookingResponse",
    # Disputes and adjustments
    "DisputeCreateRequest",
    "DisputeUpdateRequest",
    "DisputeAdjustmentCreateRequest",
    "DisputeResponse",
    "DisputeAdjustmentResponse",
    # Admin customer accounts
    "AdminCustomerListRequest",
    "AdminCustomerStatusUpdateRequest",
    "PrivacyRequestCreateRequest",
    "PrivacyRequestReviewRequest",
    "AdminCustomerListItemResponse",
    "AdminCustomerDetailResponse",
    "PrivacyRequestResponse",
    # Payouts and settlement
    "PayoutBatchGenerateRequest",
    "PayoutBatchMarkPaidRequest",
    "PayoutLineResponse",
    "PayoutBatchResponse",
    "PayoutBatchDetailResponse",
    "PayoutExportResponse",
    # Reviews moderation
    "ReviewModerationFilterRequest",
    "ReviewModerationActionRequest",
    "ReviewAggregateOverrideRequest",
    "ReviewModerationResponse",
    "HelperAggregateResponse",
    # Content policy
    "ContentBlockUpsertRequest",
    "ContentBlockResponse",
    # Insurance and risk
    "InsuranceProductUpsertRequest",
    "InsuranceEnrollmentUpsertRequest",
    "InsuranceClaimCreateRequest",
    "InsuranceClaimUpdateRequest",
    "ServiceInsuranceRuleUpdateRequest",
    "InsuranceProductResponse",
    "InsuranceEnrollmentResponse",
    "InsuranceClaimResponse",
    "ServiceInsuranceRuleResponse",
]
