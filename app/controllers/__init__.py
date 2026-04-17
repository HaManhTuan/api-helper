from app.config.constants import API_V1_PREFIX
from app.config.custom_router import APIRouter as CustomAPIRouter
from app.controllers import (
    analytics_controller,
    auth_controller,
    admin_customer_controller,
    booking_operations_controller,
    dispute_controller,
    health_controller,
    helper_kyc_controller,
    helper_moderation_controller,
    content_policy_controller,
    customer_privacy_controller,
    customer_profile_controller,
    insurance_risk_controller,
    language_controller,
    pricing_controller,
    payout_controller,
    promotion_controller,
    review_moderation_controller,
    staff_controller,
    tax_controller,
)

# Main API router using custom router
api_router = CustomAPIRouter()

def _include_system_routes() -> None:
    api_router.include_router(health_controller.router, tags=["Health"])
    api_router.include_router(language_controller.router, prefix=f"{API_V1_PREFIX}/language", tags=["Language"])
    api_router.include_router(auth_controller.public_router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
    api_router.include_router(
        auth_controller.protected_router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"], requires_auth=True
    )


def _include_admin_routes() -> None:
    admin_prefix = f"{API_V1_PREFIX}/admin"
    admin_routes = [
        (analytics_controller.router, "Admin Analytics"),
        (admin_customer_controller.router, "Admin Customers"),
        (content_policy_controller.admin_router, "Admin Content"),
        (staff_controller.router, "Admin Staff"),
        (insurance_risk_controller.router, "Admin Insurance"),
        (booking_operations_controller.router, "Admin Booking Ops"),
        (dispute_controller.router, "Admin Disputes"),
        (helper_moderation_controller.router, "Admin Helper Moderation"),
        (pricing_controller.router, "Admin Pricing"),
        (payout_controller.router, "Admin Payouts"),
        (promotion_controller.router, "Admin Promotions"),
        (review_moderation_controller.router, "Admin Reviews"),
        (tax_controller.router, "Admin Tax"),
    ]
    for router, tag in admin_routes:
        api_router.include_router(router, prefix=admin_prefix, tags=[tag], requires_auth=True)


def _include_helper_and_public_routes() -> None:
    api_router.include_router(helper_kyc_controller.router, prefix=f"{API_V1_PREFIX}", tags=["Helper KYC"], requires_auth=True)
    api_router.include_router(
        customer_profile_controller.router, prefix=f"{API_V1_PREFIX}", tags=["Customer Profile"], requires_auth=True
    )
    api_router.include_router(
        customer_privacy_controller.router, prefix=f"{API_V1_PREFIX}", tags=["Customer Privacy"], requires_auth=True
    )
    api_router.include_router(content_policy_controller.public_router, prefix=f"{API_V1_PREFIX}", tags=["Public Content"])


_include_system_routes()
_include_admin_routes()
_include_helper_and_public_routes()
