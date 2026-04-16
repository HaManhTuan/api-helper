"""
Import all models here to ensure they are registered with SQLAlchemy metadata.
This is used by Alembic for auto-generating migrations.
"""

# Import base model
from app.models.base_model import BaseModel

# Import all entity models
from app.models.booking_financial_snapshot import BookingFinancialSnapshot
from app.models.commercial_audit_log import CommercialAuditLog
from app.models.commission_rule import CommissionRule
from app.models.permission import Permission
from app.models.price_book_entry import PriceBookEntry
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.service_offering import ServiceOffering
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User

__all__ = [
    "BaseModel",
    "Role",
    "Permission",
    "RolePermission",
    "StaffAuditLog",
    "ServiceOffering",
    "PriceBookEntry",
    "CommissionRule",
    "BookingFinancialSnapshot",
    "CommercialAuditLog",
    "User",
]
