from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.booking_financial_snapshot import BookingFinancialSnapshot
from app.models.dispute import Dispute
from app.models.dispute_adjustment import DisputeAdjustment
from app.models.user import User
from app.schemas.payouts import PayoutBatchGenerateRequest, PayoutBatchMarkPaidRequest
from app.services.payout_service import payout_service


@pytest.mark.asyncio
async def test_generate_approve_export_and_mark_paid_batch(db: AsyncSession) -> None:
    finance = User(email="finance-payout@test.local", role="staff", status="active", password="secret")
    helper = User(email="helper-payout@test.local", role="helper", status="active", password="secret")
    customer = User(email="customer-payout@test.local", role="customer", status="active", password="secret")
    db.add_all([finance, helper, customer])
    await db.flush()

    booking = Booking(
        customer_id=customer.id,
        helper_id=helper.id,
        quote_id="Q-PAYOUT-1",
        status="completed",
        scheduled_start=datetime.utcnow() - timedelta(days=2),
        scheduled_end=datetime.utcnow() - timedelta(days=1),
        address_snapshot={"district": "1", "city": "hcm"},
    )
    db.add(booking)
    await db.flush()

    snapshot = BookingFinancialSnapshot(
        booking_id=booking.id,
        currency="VND",
        customer_total=120_000,
        subtotal_before_tax=120_000,
        tax_total=0,
        promotion_total=0,
        helper_total=100_000,
        platform_total=20_000,
        line_items=[],
        computed_at=datetime.utcnow() - timedelta(hours=12),
    )
    db.add(snapshot)

    dispute = Dispute(
        booking_id=booking.id,
        owner_staff_id=finance.id,
        dispute_type="quality",
        status="resolved",
        description="test",
        insurance_claim_id=None,
        opened_at=datetime.utcnow() - timedelta(hours=5),
        resolved_at=datetime.utcnow() - timedelta(hours=4),
    )
    db.add(dispute)
    await db.flush()

    adjustment = DisputeAdjustment(
        dispute_id=dispute.id,
        booking_id=booking.id,
        direction="debit",
        target_party="helper",
        amount=10_000,
        reason_code="clawback",
        note="post dispute clawback",
        created_by=finance.id,
    )
    db.add(adjustment)
    await db.commit()

    batch = await payout_service.generate_batch(
        db,
        finance,
        PayoutBatchGenerateRequest(
            period_start=datetime.utcnow() - timedelta(days=3),
            period_end=datetime.utcnow(),
            currency="VND",
        ),
    )
    assert batch.status == "pending_approval"
    assert batch.total_lines == 1
    assert batch.total_amount == 90_000

    approved = await payout_service.approve_batch(db, finance, batch.id)
    assert approved.status == "approved"

    exported = await payout_service.export_batch_csv(db, batch.id)
    assert exported["filename"].endswith(".csv")
    assert "helper_id,currency,base_amount,adjustment_amount,total_amount,booking_count" in exported["csv_content"]

    paid = await payout_service.mark_batch_paid(
        db,
        finance,
        batch.id,
        PayoutBatchMarkPaidRequest(status="paid"),
    )
    assert paid.status == "paid"
