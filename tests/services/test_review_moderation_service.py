from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.helper_profile import HelperProfile
from app.models.review import Review
from app.models.user import User
from app.repositories.concrete.helper_profile_repository import helper_profile_repository
from app.schemas.reviews import ReviewAggregateOverrideRequest, ReviewModerationActionRequest
from app.services.review_moderation_service import review_moderation_service


@pytest.mark.asyncio
async def test_hide_review_recalculates_helper_aggregate(db: AsyncSession) -> None:
    admin = User(email="admin-review@test.local", role="admin", status="active", password="secret")
    helper = User(email="helper-review@test.local", role="helper", status="active", password="secret")
    customer = User(email="customer-review@test.local", role="customer", status="active", password="secret")
    db.add_all([admin, helper, customer])
    await db.flush()

    profile = HelperProfile(
        user_id=helper.id,
        display_name="helper",
        skills=[],
        service_area={"city": "hanoi"},
        approval_status="approved",
        aggregate_rating=5.0,
        ratings_count=1,
    )
    db.add(profile)
    await db.flush()

    booking = Booking(
        customer_id=customer.id,
        helper_id=helper.id,
        quote_id="Q-REV-1",
        status="completed",
        scheduled_start=datetime.utcnow() - timedelta(days=1),
        scheduled_end=datetime.utcnow(),
        address_snapshot={"city": "hanoi"},
    )
    db.add(booking)
    await db.flush()

    review = Review(
        booking_id=booking.id,
        helper_id=helper.id,
        customer_id=customer.id,
        rating=5,
        comment="Great",
        status="visible",
    )
    db.add(review)
    await db.commit()

    hidden = await review_moderation_service.moderate_review(
        db,
        admin,
        review.id,
        ReviewModerationActionRequest(action="hide", reason_code="abuse"),
    )
    assert hidden.status == "hidden"
    profile_after_hide = await helper_profile_repository.get_by_user_id(db, helper.id)
    assert profile_after_hide is not None
    assert float(profile_after_hide.aggregate_rating) == 0.0
    assert int(profile_after_hide.ratings_count) == 0

    refreshed_profile = await review_moderation_service.override_helper_aggregate(
        db,
        admin,
        helper.id,
        ReviewAggregateOverrideRequest(aggregate_rating=4.5, ratings_count=10, reason_code="manual_review"),
    )
    assert float(refreshed_profile.aggregate_rating) == 4.5
    assert refreshed_profile.ratings_count == 10
