import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException
from app.models.user import User
from app.schemas.customer_privacy import CustomerPrivacyRequestCreateRequest
from app.services.customer_privacy_service import customer_privacy_service


@pytest.mark.asyncio
async def test_customer_submit_and_read_own_privacy_requests(db: AsyncSession) -> None:
    customer_a = User(email="customer-a-privacy@test.local", role="customer", status="active", password="secret")
    customer_b = User(email="customer-b-privacy@test.local", role="customer", status="active", password="secret")
    db.add_all([customer_a, customer_b])
    await db.commit()
    await db.refresh(customer_a)
    await db.refresh(customer_b)

    created = await customer_privacy_service.create_request(
        db,
        customer_a,
        CustomerPrivacyRequestCreateRequest(request_type="export"),
    )
    assert created.customer_id == customer_a.id
    assert created.status == "submitted"

    rows_a = await customer_privacy_service.list_own_requests(db, customer_a)
    assert len(rows_a) >= 1
    assert all(item.customer_id == customer_a.id for item in rows_a)

    own = await customer_privacy_service.get_own_request(db, customer_a, created.id)
    assert own.id == created.id

    with pytest.raises(NotFoundException):
        await customer_privacy_service.get_own_request(db, customer_b, created.id)
