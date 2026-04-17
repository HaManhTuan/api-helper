from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException, ValidationException
from app.models.helper_profile import HelperProfile
from app.models.review import Review
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User
from app.repositories.concrete.helper_profile_repository import helper_profile_repository
from app.repositories.concrete.review_repository import review_repository


class ReviewModerationService:
    async def list_reviews(self, db: AsyncSession, payload) -> List[Review]:
        return await review_repository.list_for_moderation(
            db,
            booking_id=payload.booking_id,
            helper_id=payload.helper_id,
            customer_id=payload.customer_id,
            min_rating=payload.min_rating,
            max_rating=payload.max_rating,
            status=payload.status,
            created_from=payload.created_from,
            created_to=payload.created_to,
            skip=payload.skip,
            limit=payload.limit,
        )

    async def moderate_review(self, db: AsyncSession, actor: User, review_id: str, payload) -> Review:
        review = await review_repository.get_by_id(db, review_id)
        if review is None:
            raise NotFoundException("Review not found")

        previous_status = review.status
        if payload.action == "hide":
            review.status = "hidden"
            review.flagged_reason_code = payload.reason_code
        elif payload.action == "unhide":
            review.status = "visible"
            review.flagged_reason_code = None
        elif payload.action == "flag":
            if not payload.reason_code:
                raise ValidationException("reason_code is required when flagging a review")
            review.status = "flagged"
            review.flagged_reason_code = payload.reason_code
        else:
            raise ValidationException("Unsupported moderation action")

        review.moderated_by = actor.id
        review.moderated_at = datetime.utcnow()
        db.add(review)

        await self.recalculate_helper_aggregate(db, helper_id=review.helper_id, actor=actor, reason="review_moderation")
        await self._audit(
            db,
            actor_user_id=actor.id,
            target_user_id=review.helper_id,
            action=f"review:{payload.action}",
            details=f"review_id={review.id};status={previous_status}->{review.status};reason={payload.reason_code or ''}",
        )
        await db.commit()
        await db.refresh(review)
        return review

    async def recalculate_helper_aggregate(
        self, db: AsyncSession, *, helper_id: str, actor: User, reason: str = "recalculate"
    ) -> HelperProfile:
        profile = await helper_profile_repository.get_by_user_id(db, helper_id)
        if profile is None:
            raise NotFoundException("Helper profile not found")

        avg_rating, count = await review_repository.aggregate_visible_for_helper(db, helper_id)
        profile.aggregate_rating = Decimal(str(avg_rating)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        profile.ratings_count = int(count)
        db.add(profile)
        await self._audit(
            db,
            actor_user_id=actor.id,
            target_user_id=helper_id,
            action="review:aggregate:recalculate",
            details=f"aggregate={float(profile.aggregate_rating)};count={profile.ratings_count};reason={reason}",
        )
        return profile

    async def override_helper_aggregate(self, db: AsyncSession, actor: User, helper_id: str, payload) -> HelperProfile:
        profile = await helper_profile_repository.get_by_user_id(db, helper_id)
        if profile is None:
            raise NotFoundException("Helper profile not found")
        profile.aggregate_rating = Decimal(str(payload.aggregate_rating)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        profile.ratings_count = int(payload.ratings_count)
        db.add(profile)
        await self._audit(
            db,
            actor_user_id=actor.id,
            target_user_id=helper_id,
            action="review:aggregate:override",
            details=f"aggregate={payload.aggregate_rating};count={payload.ratings_count};reason={payload.reason_code}",
        )
        await db.commit()
        await db.refresh(profile)
        return profile

    async def _audit(self, db: AsyncSession, actor_user_id: str, target_user_id: str, action: str, details: str) -> None:
        db.add(
            StaffAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action=action,
                details=details,
            )
        )


review_moderation_service = ReviewModerationService()
