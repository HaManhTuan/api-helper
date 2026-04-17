from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.insurance_claim import InsuranceClaim
from app.models.insurance_enrollment import InsuranceEnrollment
from app.models.insurance_product import InsuranceProduct
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User
from app.repositories.concrete.booking_repository import booking_repository
from app.repositories.concrete.insurance_claim_repository import insurance_claim_repository
from app.repositories.concrete.insurance_enrollment_repository import insurance_enrollment_repository
from app.repositories.concrete.insurance_product_repository import insurance_product_repository
from app.repositories.concrete.service_offering_repository import service_offering_repository


class InsuranceRiskService:
    CLAIM_STATUS = {"opened", "under_review", "accepted", "rejected", "closed"}

    async def upsert_product(self, db: AsyncSession, actor: User, product_id: Optional[str], payload) -> InsuranceProduct:
        product = await insurance_product_repository.get_by_id(db, product_id) if product_id else None
        if product is None:
            product = InsuranceProduct(name=payload.name, coverage_summary=payload.coverage_summary, premium_model=payload.premium_model)
        product.name = payload.name
        product.description = payload.description
        product.coverage_summary = payload.coverage_summary
        product.premium_model = payload.premium_model
        product.eligibility_rule = payload.eligibility_rule
        product.active = payload.active
        product.valid_from = payload.valid_from
        product.valid_to = payload.valid_to
        db.add(product)
        await db.flush()
        await self._audit(db, actor.id, actor.id, "insurance:product:upsert", f"product_id={product.id};active={product.active}")
        await db.commit()
        await db.refresh(product)
        return product

    async def list_products(self, db: AsyncSession, *, active: Optional[bool]) -> List[InsuranceProduct]:
        return await insurance_product_repository.list_products(db, active=active)

    async def upsert_enrollment(self, db: AsyncSession, actor: User, enrollment_id: Optional[str], payload) -> InsuranceEnrollment:
        enrollment = await insurance_enrollment_repository.get_by_id(db, enrollment_id) if enrollment_id else None
        if enrollment is None:
            enrollment = InsuranceEnrollment(helper_id=payload.helper_id, product_id=payload.product_id, status=payload.status)
        enrollment.helper_id = payload.helper_id
        enrollment.product_id = payload.product_id
        enrollment.status = payload.status
        enrollment.effective_from = payload.effective_from
        enrollment.effective_to = payload.effective_to
        enrollment.notes = payload.notes
        db.add(enrollment)
        await db.flush()
        await self._audit(
            db,
            actor.id,
            payload.helper_id,
            "insurance:enrollment:upsert",
            f"enrollment_id={enrollment.id};status={enrollment.status};product_id={enrollment.product_id}",
        )
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    async def list_enrollments(
        self, db: AsyncSession, *, helper_id: Optional[str], product_id: Optional[str], status: Optional[str]
    ) -> List[InsuranceEnrollment]:
        return await insurance_enrollment_repository.list_enrollments(
            db, helper_id=helper_id, product_id=product_id, status=status
        )

    async def create_claim(self, db: AsyncSession, actor: User, payload) -> InsuranceClaim:
        booking = await booking_repository.get_by_id(db, payload.booking_id)
        if booking is None:
            raise NotFoundException("Booking not found")
        claim = InsuranceClaim(
            booking_id=payload.booking_id,
            reporter_role=payload.reporter_role,
            description=payload.description,
            severity=payload.severity,
            status="opened",
        )
        db.add(claim)
        await db.flush()
        await self._audit(db, actor.id, actor.id, "insurance:claim:create", f"claim_id={claim.id};booking_id={claim.booking_id}")
        await db.commit()
        await db.refresh(claim)
        return claim

    async def update_claim(self, db: AsyncSession, actor: User, claim_id: str, payload) -> InsuranceClaim:
        claim = await insurance_claim_repository.get_by_id(db, claim_id)
        if claim is None:
            raise NotFoundException("Insurance claim not found")
        if claim.status == "closed":
            raise ConflictException("Closed claim cannot be updated")
        if payload.status is not None:
            if payload.status not in self.CLAIM_STATUS:
                raise ValidationException("Invalid claim status")
            claim.status = payload.status
        if payload.resolution_notes is not None:
            claim.resolution_notes = payload.resolution_notes
        if payload.payout_amount is not None:
            claim.payout_amount = payload.payout_amount
        db.add(claim)
        await self._audit(db, actor.id, actor.id, "insurance:claim:update", f"claim_id={claim.id};status={claim.status}")
        await db.commit()
        await db.refresh(claim)
        return claim

    async def list_claims(self, db: AsyncSession, *, status: Optional[str], booking_id: Optional[str]) -> List[InsuranceClaim]:
        return await insurance_claim_repository.list_claims(db, status=status, booking_id=booking_id)

    async def update_service_rule(self, db: AsyncSession, actor: User, service_id: str, payload):
        service = await service_offering_repository.get_by_id(db, service_id)
        if service is None:
            raise NotFoundException("Service offering not found")
        service.insurance_required = payload.insurance_required
        service.insurance_enforcement = payload.insurance_enforcement
        db.add(service)
        await self._audit(
            db,
            actor.id,
            actor.id,
            "insurance:service-rule:update",
            f"service_id={service.id};required={service.insurance_required};enforcement={service.insurance_enforcement}",
        )
        await db.commit()
        await db.refresh(service)
        return service

    async def assert_helper_assignment_allowed(
        self, db: AsyncSession, *, helper_id: str, service_id: str, at: Optional[datetime] = None
    ) -> None:
        service = await service_offering_repository.get_by_id(db, service_id)
        if service is None or not service.insurance_required:
            return
        covered = await insurance_enrollment_repository.has_active_coverage(db, helper_id=helper_id, at=at or datetime.utcnow())
        if not covered and service.insurance_enforcement == "hard":
            raise ValidationException("Helper does not have active insurance coverage")

    async def _audit(self, db: AsyncSession, actor_user_id: str, target_user_id: str, action: str, details: str) -> None:
        db.add(
            StaffAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action=action,
                details=details,
            )
        )


insurance_risk_service = InsuranceRiskService()
