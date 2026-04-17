from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.user import User
from app.schemas.disputes import DisputeAdjustmentCreateRequest, DisputeCreateRequest, DisputeUpdateRequest
from app.services.dispute_service import dispute_service


@pytest.mark.asyncio
async def test_create_dispute_and_adjustment(db: AsyncSession) -> None:
    admin = User(email="admin-dispute@test.local", role="admin", status="active", password="secret")
    customer = User(email="customer-dispute@test.local", role="customer", status="active", password="secret")
    db.add_all([admin, customer])
    await db.flush()

    booking = Booking(
        customer_id=customer.id,
        helper_id=None,
        quote_id="Q-DISPUTE-1",
        status="completed",
        scheduled_start=datetime.utcnow() - timedelta(days=1),
        scheduled_end=datetime.utcnow(),
        address_snapshot={"district": "Dong Da", "city": "hanoi"},
    )
    db.add(booking)
    await db.commit()

    dispute = await dispute_service.create_dispute(
        db,
        admin,
        DisputeCreateRequest(
            booking_id=booking.id,
            owner_staff_id=admin.id,
            dispute_type="quality",
            description="Customer reported poor quality",
        ),
    )
    assert dispute.booking_id == booking.id
    assert dispute.status == "open"

    updated = await dispute_service.update_dispute(
        db,
        admin,
        dispute.id,
        DisputeUpdateRequest(status="investigating"),
    )
    assert updated.status == "investigating"

    adjustment = await dispute_service.create_adjustment(
        db,
        admin,
        dispute.id,
        DisputeAdjustmentCreateRequest(
            direction="credit",
            target_party="customer",
            amount=50_000,
            reason_code="goodwill_refund",
            note="Refund after dispute investigation",
        ),
    )
    assert adjustment.booking_id == booking.id
    assert adjustment.amount == 50_000
    assert adjustment.target_party == "customer"
