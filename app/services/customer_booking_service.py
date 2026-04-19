from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.booking import Booking
from app.models.booking_financial_snapshot import BookingFinancialSnapshot
from app.models.customer_quote import CustomerQuote
from app.models.user import User
from app.repositories.concrete.booking_repository import booking_repository
from app.repositories.concrete.customer_quote_repository import customer_quote_repository
from app.repositories.concrete.promotion_repository import promotion_repository
from app.schemas.pricing import BookingSnapshotComputeRequest
from app.services.pricing_service import pricing_service


class CustomerBookingService:
    HANOI_CITY_ALIASES = {"hanoi", "ha noi", "ha_noi", "hà nội", "ha-noi"}
    CUSTOMER_CANCELLABLE_STATUSES = {"pending", "accepted"}
    CANCELLATION_CUTOFF_HOURS = 24
    QUOTE_TTL_MINUTES = 30

    async def request_quote(self, db: AsyncSession, customer: User, payload) -> tuple[CustomerQuote, BookingFinancialSnapshot]:
        if not payload.line_items:
            raise ValidationException("line_items is required")
        self._validate_hanoi_address(payload.address_snapshot)
        await self._validate_promotion_code(db, payload.promotion_code, payload.scheduled_start)

        quote_code = str(uuid4())
        quote_booking_id = f"quote-{quote_code}"
        snapshot = await pricing_service.compute_and_persist_snapshot(
            db=db,
            actor=customer,
            payload=BookingSnapshotComputeRequest(
                booking_id=quote_booking_id,
                customer_id=customer.id,
                at=payload.scheduled_start,
                quote_id=quote_code,
                promotion_code=payload.promotion_code,
                surge_multiplier=payload.surge_multiplier,
                line_items=payload.line_items,
            ),
        )

        quote = CustomerQuote(
            customer_id=customer.id,
            quote_code=quote_code,
            currency=snapshot.currency,
            promotion_code=payload.promotion_code,
            surge_multiplier=str(payload.surge_multiplier),
            line_items=[item.model_dump(mode="json") for item in payload.line_items],
            address_snapshot=payload.address_snapshot,
            scheduled_start=payload.scheduled_start,
            subtotal_before_tax=snapshot.subtotal_before_tax,
            tax_total=snapshot.tax_total,
            promotion_total=snapshot.promotion_total,
            customer_total=snapshot.customer_total,
            expires_at=datetime.utcnow() + timedelta(minutes=self.QUOTE_TTL_MINUTES),
        )
        db.add(quote)
        await db.commit()
        await db.refresh(quote)
        return quote, snapshot

    async def create_booking(self, db: AsyncSession, customer: User, payload) -> tuple[Booking, BookingFinancialSnapshot]:
        self._validate_hanoi_address(payload.address_snapshot)
        quote = await customer_quote_repository.get_active_by_code(db, customer.id, payload.quote_id, datetime.utcnow())
        if quote is None:
            raise ValidationException("quote_id is invalid or expired")
        if quote.line_items != [item.model_dump(mode="json") for item in payload.line_items]:
            raise ConflictException("Booking payload does not match quoted line items")

        booking = Booking(
            customer_id=customer.id,
            helper_id=None,
            quote_id=payload.quote_id,
            line_items=quote.line_items,
            status="pending",
            scheduled_start=payload.scheduled_start,
            scheduled_end=payload.scheduled_end,
            address_snapshot=payload.address_snapshot,
        )
        db.add(booking)
        await db.flush()

        snapshot = await pricing_service.compute_and_persist_snapshot(
            db=db,
            actor=customer,
            payload=BookingSnapshotComputeRequest(
                booking_id=booking.id,
                customer_id=customer.id,
                at=payload.scheduled_start,
                quote_id=payload.quote_id,
                promotion_code=quote.promotion_code,
                surge_multiplier=float(quote.surge_multiplier),
                line_items=payload.line_items,
            ),
        )
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking, snapshot

    async def list_own_bookings(self, db: AsyncSession, customer: User, *, status: str | None, skip: int, limit: int) -> list[Booking]:
        return await booking_repository.list_by_customer(db, customer_id=customer.id, status=status, skip=skip, limit=limit)

    async def get_own_booking(self, db: AsyncSession, customer: User, booking_id: str) -> tuple[Booking, BookingFinancialSnapshot | None]:
        booking = await booking_repository.get_by_id_and_customer(db, booking_id, customer.id)
        if booking is None:
            raise NotFoundException("Booking not found")
        snapshot_row = await db.execute(
            select(BookingFinancialSnapshot).where(
                BookingFinancialSnapshot.deleted_at.is_(None),
                BookingFinancialSnapshot.booking_id == booking.id,
            )
        )
        return booking, snapshot_row.scalar_one_or_none()

    async def cancel_own_booking(self, db: AsyncSession, customer: User, booking_id: str, reason_code: str) -> Booking:
        booking = await booking_repository.get_by_id_and_customer(db, booking_id, customer.id)
        if booking is None:
            raise NotFoundException("Booking not found")
        if booking.status not in self.CUSTOMER_CANCELLABLE_STATUSES:
            raise ConflictException("Booking cannot be cancelled in current state")
        if booking.scheduled_start <= datetime.utcnow() + timedelta(hours=self.CANCELLATION_CUTOFF_HOURS):
            raise ConflictException("Booking cancellation window has passed")
        booking.status = "cancelled"
        booking.cancellation_reason_code = reason_code
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking

    def _validate_hanoi_address(self, address_snapshot: dict) -> None:
        city = str(address_snapshot.get("city", "")).strip().lower()
        if city not in self.HANOI_CITY_ALIASES:
            raise ValidationException("Only Hanoi addresses are supported")

    async def _validate_promotion_code(self, db: AsyncSession, promotion_code: str | None, at: datetime) -> None:
        if not promotion_code:
            return
        promo = await promotion_repository.get_by_code(db, promotion_code)
        if promo is None or not promo.active or promo.deleted_at is not None:
            raise ValidationException("Promotion code is invalid")
        if at < promo.starts_at or (promo.ends_at is not None and at > promo.ends_at):
            raise ValidationException("Promotion code is not active")


customer_booking_service = CustomerBookingService()
