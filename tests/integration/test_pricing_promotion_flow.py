from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commission_rule import CommissionRule
from app.models.price_book_entry import PriceBookEntry
from app.models.promotion import Promotion
from app.models.promotion_redemption import PromotionRedemption
from app.models.service_offering import ServiceOffering
from app.models.user import User
from app.schemas.pricing import BookingLineItemPriceRequest, BookingSnapshotComputeRequest
from app.services.pricing_service import pricing_service


@pytest.mark.asyncio
async def test_compute_snapshot_with_promotion_surge_commission(db: AsyncSession) -> None:
    now = datetime.utcnow()

    actor = User(email="admin-pricing@test.local", role="admin", status="active", password="secret")
    db.add(actor)

    service = ServiceOffering(
        code="CLEAN_STD",
        name="Cleaning Standard",
        description="Standard cleaning package",
        unit="hour",
        active=True,
        tags=[],
        meta={},
    )
    db.add(service)
    await db.flush()

    db.add(
        PriceBookEntry(
            service_offering_id=service.id,
            variant_code=None,
            zone_code=None,
            currency="VND",
            customer_price=100_000,
            reference_cost=70_000,
            effective_from=now - timedelta(days=1),
            effective_to=None,
            priority=10,
            active=True,
        )
    )
    db.add(
        CommissionRule(
            service_offering_id=service.id,
            helper_percent=70,
            platform_percent=30,
            fixed_platform_fee=0,
            fixed_helper_fee=0,
            effective_from=now - timedelta(days=1),
            effective_to=None,
            priority=10,
            active=True,
        )
    )
    db.add(
        Promotion(
            code="PROMO20",
            promotion_type="percent",
            service_id=service.id,
            discount_percent=20,
            discount_amount=None,
            max_redemptions=100,
            per_user_limit=10,
            stack_rule="surge_then_promotion",
            effective_from=now - timedelta(days=1),
            effective_to=now + timedelta(days=2),
            active=True,
        )
    )
    await db.commit()

    payload = BookingSnapshotComputeRequest(
        booking_id="BOOKING-001",
        customer_id="CUSTOMER-001",
        quote_id="QUOTE-001",
        at=now,
        promotion_code="PROMO20",
        surge_multiplier=1.2,
        line_items=[BookingLineItemPriceRequest(service_code="CLEAN_STD", quantity=1)],
    )
    snapshot = await pricing_service.compute_and_persist_snapshot(db=db, actor=actor, payload=payload)

    assert snapshot.customer_total == 96_000
    assert snapshot.promotion_total == 24_000
    assert snapshot.helper_total == 67_200
    assert snapshot.platform_total == 28_800
    assert snapshot.customer_total == snapshot.helper_total + snapshot.platform_total

    redemption_rows = await db.execute(
        PromotionRedemption.__table__.select().where(PromotionRedemption.booking_id == "BOOKING-001")
    )
    redemptions = redemption_rows.fetchall()
    assert len(redemptions) == 1
    assert int(redemptions[0].redeemed_amount) == 24_000
