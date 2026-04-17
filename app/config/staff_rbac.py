"""
Common internal RBAC catalog for staff/admin operations.

This catalog is system-managed and should be seeded automatically.
"""

from typing import Dict, List

COMMON_PERMISSIONS: List[str] = [
    "staff:manage",
    "users:read",
    "bookings:read:all",
    "bookings:assign",
    "pricing:write",
    "helpers:moderate",
    "kyc:review",
    "payouts:read",
    "payouts:approve",
    "audit:read",
    "reports:export",
]

COMMON_ROLES: Dict[str, Dict[str, object]] = {
    "super_admin": {
        "name": "Super Admin",
        "description": "Full internal control over staff and operations.",
        "permissions": COMMON_PERMISSIONS,
    },
    "operations": {
        "name": "Operations",
        "description": "Booking operations and customer support workflows.",
        "permissions": ["users:read", "bookings:read:all", "bookings:assign", "helpers:moderate", "kyc:review"],
    },
    "finance": {
        "name": "Finance",
        "description": "Payout and financial approval operations.",
        "permissions": ["payouts:read", "payouts:approve", "reports:export"],
    },
    "support": {
        "name": "Support",
        "description": "Read-focused operational support access.",
        "permissions": ["users:read", "bookings:read:all"],
    },
    "readonly": {
        "name": "Read Only",
        "description": "Audit and reporting read-only access.",
        "permissions": ["audit:read"],
    },
}

