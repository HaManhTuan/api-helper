from app.config.constants import API_V1_PREFIX
from app.config.custom_router import APIRouter as CustomAPIRouter
from app.controllers import (
    auth_controller,
    admin_customer_controller,
    booking_operations_controller,
    dispute_controller,
    health_controller,
    helper_kyc_controller,
    helper_moderation_controller,
    language_controller,
    pricing_controller,
    promotion_controller,
    staff_controller,
    tax_controller,
)

# Main API router using custom router
api_router = CustomAPIRouter()

# Include sub-routers
# System routers (auth, health, language) - placed at top
api_router.include_router(health_controller.router, tags=["Health"])
# Language routes
api_router.include_router(language_controller.router, prefix=f"{API_V1_PREFIX}/language", tags=["Language"])
# Public auth routes (login, register)
api_router.include_router(auth_controller.public_router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
# Protected auth routes (profile)
api_router.include_router(
    auth_controller.protected_router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"], requires_auth=True
)
api_router.include_router(
    admin_customer_controller.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin Customers"], requires_auth=True
)
api_router.include_router(
    staff_controller.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin Staff"], requires_auth=True
)
api_router.include_router(
    booking_operations_controller.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin Booking Ops"], requires_auth=True
)
api_router.include_router(
    dispute_controller.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin Disputes"], requires_auth=True
)
api_router.include_router(
    helper_moderation_controller.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin Helper Moderation"], requires_auth=True
)
api_router.include_router(
    pricing_controller.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin Pricing"], requires_auth=True
)
api_router.include_router(
    promotion_controller.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin Promotions"], requires_auth=True
)
api_router.include_router(
    tax_controller.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin Tax"], requires_auth=True
)
api_router.include_router(
    helper_kyc_controller.router, prefix=f"{API_V1_PREFIX}", tags=["Helper KYC"], requires_auth=True
)
