import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.customers import (
    AdminCustomerListRequest,
    AdminCustomerStatusUpdateRequest,
    PrivacyRequestCreateRequest,
    PrivacyRequestReviewRequest,
)
from app.services.admin_customer_service import admin_customer_service


@pytest.mark.asyncio
async def test_admin_customer_suspend_reactivate_and_privacy_request(db: AsyncSession) -> None:
    admin = User(email="admin-customer@test.local", role="admin", status="active", password="secret")
    customer = User(email="customer-customer@test.local", role="customer", status="active", password="secret")
    db.add_all([admin, customer])
    await db.commit()
    await db.refresh(admin)
    await db.refresh(customer)

    customers, total = await admin_customer_service.list_customers(db, AdminCustomerListRequest(page=1, page_size=20))
    assert total >= 1
    assert any(item.id == customer.id for item in customers)

    suspended = await admin_customer_service.suspend_customer(
        db,
        admin,
        customer.id,
        AdminCustomerStatusUpdateRequest(reason_code="fraud", note="suspicious behavior"),
    )
    assert suspended.status == "suspended"

    reactivated = await admin_customer_service.reactivate_customer(
        db,
        admin,
        customer.id,
        AdminCustomerStatusUpdateRequest(reason_code="review_passed", note="manual review approved"),
    )
    assert reactivated.status == "active"

    privacy_request = await admin_customer_service.create_privacy_request(
        db,
        admin,
        customer.id,
        PrivacyRequestCreateRequest(request_type="export"),
    )
    assert privacy_request.status == "submitted"

    reviewed = await admin_customer_service.review_privacy_request(
        db,
        admin,
        privacy_request.id,
        PrivacyRequestReviewRequest(status="in_review"),
    )
    assert reviewed.status == "in_review"
