from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.dispute import Dispute
from app.models.dispute_adjustment import DisputeAdjustment
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User
from app.repositories.concrete.booking_repository import booking_repository
from app.repositories.concrete.dispute_adjustment_repository import dispute_adjustment_repository
from app.repositories.concrete.dispute_repository import dispute_repository


class DisputeService:
    VALID_STATUSES = {"open", "investigating", "resolved", "closed"}

    async def list_disputes(
        self, db: AsyncSession, *, status: Optional[str], booking_id: Optional[str], owner_staff_id: Optional[str]
    ) -> List[Dispute]:
        return await dispute_repository.list_cases(
            db,
            status=status,
            booking_id=booking_id,
            owner_staff_id=owner_staff_id,
        )

    async def get_dispute(self, db: AsyncSession, dispute_id: str) -> Dispute:
        dispute = await dispute_repository.get_by_id(db, dispute_id)
        if dispute is None:
            raise NotFoundException("Dispute not found")
        return dispute

    async def create_dispute(self, db: AsyncSession, actor: User, payload) -> Dispute:
        booking = await booking_repository.get_by_id(db, payload.booking_id)
        if booking is None:
            raise NotFoundException("Booking not found")

        dispute = Dispute(
            booking_id=payload.booking_id,
            owner_staff_id=payload.owner_staff_id,
            dispute_type=payload.dispute_type,
            status="open",
            description=payload.description,
            insurance_claim_id=payload.insurance_claim_id,
            opened_at=datetime.utcnow(),
            resolved_at=None,
        )
        db.add(dispute)
        await db.flush()
        await self._audit(db, actor.id, dispute.id, "dispute:create", f"booking_id={payload.booking_id}")
        await db.commit()
        await db.refresh(dispute)
        return dispute

    async def update_dispute(self, db: AsyncSession, actor: User, dispute_id: str, payload) -> Dispute:
        dispute = await self.get_dispute(db, dispute_id)
        before_status = dispute.status

        if payload.status is not None:
            if payload.status not in self.VALID_STATUSES:
                raise ValidationException("Invalid dispute status")
            dispute.status = payload.status
            if payload.status in {"resolved", "closed"} and dispute.resolved_at is None:
                dispute.resolved_at = datetime.utcnow()
            if payload.status in {"open", "investigating"}:
                dispute.resolved_at = None

        if payload.owner_staff_id is not None:
            dispute.owner_staff_id = payload.owner_staff_id
        if payload.dispute_type is not None:
            dispute.dispute_type = payload.dispute_type
        if payload.description is not None:
            dispute.description = payload.description
        if payload.insurance_claim_id is not None:
            dispute.insurance_claim_id = payload.insurance_claim_id

        db.add(dispute)
        await self._audit(
            db,
            actor.id,
            dispute.id,
            "dispute:update",
            f"status={before_status}->{dispute.status}",
        )
        await db.commit()
        await db.refresh(dispute)
        return dispute

    async def create_adjustment(self, db: AsyncSession, actor: User, dispute_id: str, payload) -> DisputeAdjustment:
        dispute = await self.get_dispute(db, dispute_id)
        booking = await booking_repository.get_by_id(db, dispute.booking_id)
        if booking is None:
            raise NotFoundException("Booking not found")
        if dispute.status == "closed":
            raise ConflictException("Cannot add adjustment to closed dispute")

        adjustment = DisputeAdjustment(
            dispute_id=dispute.id,
            booking_id=dispute.booking_id,
            direction=payload.direction,
            target_party=payload.target_party,
            amount=payload.amount,
            reason_code=payload.reason_code,
            note=payload.note,
            created_by=actor.id,
        )
        db.add(adjustment)
        await db.flush()
        await self._audit(
            db,
            actor.id,
            dispute.id,
            "adjustment:create",
            f"adjustment_id={adjustment.id};direction={payload.direction};target={payload.target_party};amount={payload.amount}",
        )
        await db.commit()
        await db.refresh(adjustment)
        return adjustment

    async def list_adjustments(self, db: AsyncSession, dispute_id: str) -> List[DisputeAdjustment]:
        _ = await self.get_dispute(db, dispute_id)
        return await dispute_adjustment_repository.list_by_dispute(db, dispute_id)

    async def _audit(self, db: AsyncSession, actor_user_id: str, target_id: str, action: str, details: str) -> None:
        db.add(
            StaffAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_id,
                action=action,
                details=details,
            )
        )


dispute_service = DisputeService()
