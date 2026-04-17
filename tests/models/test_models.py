"""
Module to explicitly import all models to ensure they're properly registered with SQLAlchemy metadata.
This module is imported by the conftest.py to ensure all models are available for table creation.
"""

# Import all model classes here to ensure they're registered with Base.metadata
from app.models import (
    Booking,
    BookingFinancialSnapshot,
    CommercialAuditLog,
    CommissionRule,
    Dispute,
    DisputeAdjustment,
    Permission,
    PayoutBatch,
    PayoutLine,
    PriceBookEntry,
    PrivacyRequest,
    PrivacyRequestEvent,
    Promotion,
    PromotionRedemption,
    Role,
    RolePermission,
    ServiceOffering,
    StaffAuditLog,
    TaxConfig,
    TaxRule,
)
from app.models.base_model import BaseModel
from app.models.user import User

# Add any other models here

# List of all model classes for reference
__all__ = [
    "BaseModel",
    "User",
    "Role",
    "Permission",
    "PayoutBatch",
    "PayoutLine",
    "RolePermission",
    "StaffAuditLog",
    "ServiceOffering",
    "PriceBookEntry",
    "PrivacyRequest",
    "PrivacyRequestEvent",
    "CommissionRule",
    "Promotion",
    "PromotionRedemption",
    "BookingFinancialSnapshot",
    "Dispute",
    "DisputeAdjustment",
    "CommercialAuditLog",
    "TaxRule",
    "TaxConfig",
    "Booking",
]
