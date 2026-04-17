from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.booking import Booking
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User
from app.repositories.concrete.booking_repository import booking_repository
from app.services.helper_moderation_service import helper_moderation_service
from app.services.user_service import user_service


class BookingOperationsService:
    ASSIGNABLE_STATUSES = {"pending"}
    REASSIGNABLE_STATUSES = {"pending", "accepted", "in-progress"}
    ADMIN_CANCELLABLE_STATUSES = {"pending", "accepted", "in-progress"}

    async def list_bookings(self, db: AsyncSession, payload):
        return await booking_repository.list_with_filters(
            db,
            status=payload.status,
            customer_id=payload.customer_id,
            helper_id=payload.helper_id,
            scheduled_from=payload.scheduled_from,
            scheduled_to=payload.scheduled_to,
            skip=payload.skip,
            limit=payload.limit,
        )

    async def get_booking(self, db: AsyncSession, booking_id: str) -> Booking:
        booking = await booking_repository.get_by_id(db, booking_id)
        if booking is None:
            raise NotFoundException("Booking not found")
        return booking

    async def assign_booking(self, db: AsyncSession, actor: User, booking_id: str, helper_id: str) -> Booking:
        booking = await self.get_booking(db, booking_id)
        if booking.status not in self.ASSIGNABLE_STATUSES:
            raise ConflictException("Booking is not in assignable state")

        helper = await user_service.get_by_id(db, id=helper_id)
        if helper is None or helper.role != "helper":
            raise ValidationException("Helper is invalid")
        await helper_moderation_service.assert_helper_eligible_for_accept(db, helper.id)

        booking.helper_id = helper.id
        booking.status = "accepted"
        booking.reassignment_reason_code = None
        db.add(booking)
        await self._audit(db, actor.id, booking.id, "booking:assign", f"helper_id={helper.id}")
        await db.commit()
        await db.refresh(booking)
        return booking

    async def reassign_booking(
        self, db: AsyncSession, actor: User, booking_id: str, helper_id: Optional[str], reason_code: Optional[str]
    ) -> Booking:
        booking = await self.get_booking(db, booking_id)
        if booking.status not in self.REASSIGNABLE_STATUSES:
            raise ConflictException("Booking is not in reassignable state")

        previous_helper_id = booking.helper_id
        if helper_id:
            helper = await user_service.get_by_id(db, id=helper_id)
            if helper is None or helper.role != "helper":
                raise ValidationException("Helper is invalid")
            await helper_moderation_service.assert_helper_eligible_for_accept(db, helper.id)
            booking.helper_id = helper.id
            booking.status = "accepted"
        else:
            booking.helper_id = None
            booking.status = "pending"

        booking.reassignment_reason_code = reason_code
        db.add(booking)
        await self._audit(
            db,
            actor.id,
            booking.id,
            "booking:reassign",
            f"from={previous_helper_id or ''};to={booking.helper_id or ''};reason={reason_code or ''}",
        )
        await db.commit()
        await db.refresh(booking)
        return booking

    async def cancel_booking(self, db: AsyncSession, actor: User, booking_id: str, reason_code: str) -> Booking:
        booking = await self.get_booking(db, booking_id)
        if booking.status not in self.ADMIN_CANCELLABLE_STATUSES:
            raise ConflictException("Booking cannot be cancelled in current state")
        booking.status = "cancelled"
        booking.cancellation_reason_code = reason_code
        db.add(booking)
        await self._audit(db, actor.id, booking.id, "booking:cancel", f"reason={reason_code}")
        await db.commit()
        await db.refresh(booking)
        return booking

    async def _audit(self, db: AsyncSession, actor_user_id: str, booking_id: str, action: str, details: str) -> None:
        db.add(
            StaffAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=booking_id,
                action=action,
                details=details,
            )
        )


booking_operations_service = BookingOperationsService()
