"""
Import all models here to ensure they are registered with SQLAlchemy metadata.
This is used by Alembic for auto-generating migrations.
"""

# Import base model
from app.models.base_model import BaseModel

# Import all entity models
from app.models.booking import Booking
from app.models.booking_financial_snapshot import BookingFinancialSnapshot
from app.models.commercial_audit_log import CommercialAuditLog
from app.models.commission_rule import CommissionRule
from app.models.dispute import Dispute
from app.models.dispute_adjustment import DisputeAdjustment
from app.models.helper_document import HelperDocument
from app.models.helper_document_type import HelperDocumentType
from app.models.helper_profile import HelperProfile
from app.models.permission import Permission
from app.models.price_book_entry import PriceBookEntry
from app.models.payout_batch import PayoutBatch
from app.models.payout_line import PayoutLine
from app.models.privacy_request import PrivacyRequest
from app.models.privacy_request_event import PrivacyRequestEvent
from app.models.promotion import Promotion
from app.models.promotion_redemption import PromotionRedemption
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.service_offering import ServiceOffering
from app.models.staff_audit_log import StaffAuditLog
from app.models.tax_config import TaxConfig
from app.models.tax_rule import TaxRule
from app.models.user import User

__all__ = [
    "BaseModel",
    "Role",
    "Permission",
    "RolePermission",
    "StaffAuditLog",
    "ServiceOffering",
    "Booking",
    "PriceBookEntry",
    "PayoutBatch",
    "PayoutLine",
    "PrivacyRequest",
    "PrivacyRequestEvent",
    "CommissionRule",
    "Dispute",
    "DisputeAdjustment",
    "HelperProfile",
    "HelperDocumentType",
    "HelperDocument",
    "Promotion",
    "PromotionRedemption",
    "BookingFinancialSnapshot",
    "CommercialAuditLog",
    "TaxRule",
    "TaxConfig",
    "User",
]
