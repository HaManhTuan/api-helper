from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.booking_financial_snapshot import BookingFinancialSnapshot
from app.models.user import User
from app.schemas.analytics import ReportExportRequest
from app.services.analytics_service import analytics_service


@pytest.mark.asyncio
async def test_analytics_timeseries_revenue_and_export(db: AsyncSession) -> None:
    staff = User(email="analytics-staff@test.local", role="staff", status="active", password="secret")
    customer = User(email="analytics-customer@test.local", role="customer", status="active", password="secret")
    helper = User(email="analytics-helper@test.local", role="helper", status="active", password="secret")
    db.add_all([staff, customer, helper])
    await db.flush()

    created_at = datetime.utcnow() - timedelta(days=1)
    booking = Booking(
        customer_id=customer.id,
        helper_id=helper.id,
        quote_id="Q-ANL-1",
        status="completed",
        scheduled_start=created_at,
        scheduled_end=created_at + timedelta(hours=2),
        address_snapshot={"district": "Dong Da", "city": "hanoi"},
    )
    db.add(booking)
    await db.flush()
    booking.created_at = created_at
    db.add(booking)

    snap = BookingFinancialSnapshot(
        booking_id=booking.id,
        currency="VND",
        customer_total=120_000,
        subtotal_before_tax=120_000,
        tax_total=0,
        promotion_total=10_000,
        helper_total=90_000,
        platform_total=20_000,
        line_items=[],
        computed_at=created_at + timedelta(hours=1),
    )
    db.add(snap)
    await db.commit()

    start_at = datetime.utcnow() - timedelta(days=7)
    end_at = datetime.utcnow()
    ts = await analytics_service.bookings_timeseries(db, start_at=start_at, end_at=end_at)
    assert len(ts) >= 1
    assert sum(row["created"] for row in ts) >= 1

    report = await analytics_service.revenue_report(db, start_at=start_at, end_at=end_at, group_by=None)
    assert report["summary"]["gmv_total"] == 120_000
    assert report["summary"]["platform_fee_total"] == 20_000

    job = await analytics_service.create_export_job(
        db,
        actor=staff,
        payload=ReportExportRequest(report_type="revenue", start_at=start_at, end_at=end_at),
    )
    assert job.status == "completed"
    assert job.file_ref is not None
