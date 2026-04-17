from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException
from app.models.booking import Booking
from app.models.helper_document import HelperDocument
from app.models.helper_document_type import HelperDocumentType
from app.models.helper_profile import HelperProfile
from app.models.user import User
from app.services.booking_operations_service import booking_operations_service


@pytest.mark.asyncio
async def test_assign_pending_booking_with_eligible_helper(db: AsyncSession) -> None:
    admin = User(email="admin-booking@test.local", role="admin", status="active", password="secret")
    customer = User(email="customer-booking@test.local", role="customer", status="active", password="secret")
    helper = User(email="helper-booking@test.local", role="helper", status="active", password="secret")
    db.add_all([admin, customer, helper])
    await db.flush()

    db.add(
        HelperProfile(
            user_id=helper.id,
            display_name="Helper Assignable",
            skills=[],
            service_area={"city": "hanoi"},
            approval_status="approved",
            approved_at=datetime.utcnow(),
            approved_by=admin.id,
        )
    )
    db.add(HelperDocumentType(code="citizen_id", name="Citizen ID", required=True, active=True, sort_order=1))
    db.add(
        HelperDocument(
            helper_id=helper.id,
            document_type="citizen_id",
            storage_ref="helpers/test/citizen_id.pdf",
            mime_type="application/pdf",
            file_size_bytes=1000,
            status="approved",
            reviewed_by=admin.id,
            reviewed_at=datetime.utcnow(),
        )
    )
    booking = Booking(
        customer_id=customer.id,
        helper_id=None,
        quote_id="Q-BOOKING-1",
        status="pending",
        scheduled_start=datetime.utcnow() + timedelta(days=1),
        scheduled_end=None,
        address_snapshot={"district": "Ba Dinh", "city": "hanoi"},
    )
    db.add(booking)
    await db.commit()

    updated = await booking_operations_service.assign_booking(db, admin, booking.id, helper.id)
    assert updated.status == "accepted"
    assert updated.helper_id == helper.id


@pytest.mark.asyncio
async def test_cannot_assign_non_pending_booking(db: AsyncSession) -> None:
    admin = User(email="admin-booking2@test.local", role="admin", status="active", password="secret")
    customer = User(email="customer-booking2@test.local", role="customer", status="active", password="secret")
    helper = User(email="helper-booking2@test.local", role="helper", status="active", password="secret")
    db.add_all([admin, customer, helper])
    await db.flush()

    booking = Booking(
        customer_id=customer.id,
        helper_id=helper.id,
        quote_id="Q-BOOKING-2",
        status="accepted",
        scheduled_start=datetime.utcnow() + timedelta(days=1),
        scheduled_end=None,
        address_snapshot={"district": "Cau Giay", "city": "hanoi"},
    )
    db.add(booking)
    await db.commit()

    with pytest.raises(ConflictException):
        await booking_operations_service.assign_booking(db, admin, booking.id, helper.id)
