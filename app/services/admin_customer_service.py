from datetime import datetime
from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException, ValidationException
from app.models.privacy_request import PrivacyRequest
from app.models.privacy_request_event import PrivacyRequestEvent
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User
from app.repositories.concrete.privacy_request_repository import privacy_request_repository
from app.services.user_service import user_service


class AdminCustomerService:
    VALID_PRIVACY_STATUS_TRANSITIONS = {
        "submitted": {"in_review", "cancelled"},
        "in_review": {"approved", "rejected", "cancelled"},
        "approved": {"completed", "cancelled"},
        "rejected": {"in_review", "cancelled"},
        "completed": set(),
        "cancelled": set(),
    }

    async def list_customers(self, db: AsyncSession, payload) -> Tuple[List[User], int]:
        return await user_service.repository.list_customers_paginated(
            db,
            page=payload.page,
            page_size=payload.page_size,
            search=payload.search,
            status=payload.status,
        )

    async def get_customer_detail(self, db: AsyncSession, customer_id: str) -> tuple[User, dict]:
        customer = await self._get_customer_or_404(db, customer_id)
        booking_counts = await user_service.repository.count_customer_bookings(db, customer_id=customer.id)
        return customer, booking_counts

    async def suspend_customer(self, db: AsyncSession, actor: User, customer_id: str, payload) -> User:
        customer = await self._get_customer_or_404(db, customer_id)
        customer.status = "suspended"
        db.add(customer)
        await self._audit(
            db,
            actor.id,
            customer.id,
            "customer:suspend",
            f"reason_code={payload.reason_code};note={payload.note or ''}",
        )
        await db.commit()
        await db.refresh(customer)
        return customer

    async def reactivate_customer(self, db: AsyncSession, actor: User, customer_id: str, payload) -> User:
        customer = await self._get_customer_or_404(db, customer_id)
        customer.status = "active"
        db.add(customer)
        await self._audit(
            db,
            actor.id,
            customer.id,
            "customer:reactivate",
            f"reason_code={payload.reason_code};note={payload.note or ''}",
        )
        await db.commit()
        await db.refresh(customer)
        return customer

    async def create_privacy_request(self, db: AsyncSession, actor: User, customer_id: str, payload) -> PrivacyRequest:
        customer = await self._get_customer_or_404(db, customer_id)
        req = PrivacyRequest(
            customer_id=customer.id,
            request_type=payload.request_type,
            status="submitted",
            legal_basis=payload.legal_basis,
            requested_payload=payload.requested_payload,
        )
        db.add(req)
        await db.flush()
        await self._append_privacy_event(
            db=db,
            privacy_request_id=req.id,
            event_type="submitted",
            from_status=None,
            to_status=req.status,
            actor_user_id=actor.id,
            metadata={"request_type": payload.request_type},
        )
        await self._audit(db, actor.id, customer.id, "customer:privacy-request:create", f"request_id={req.id}")
        await db.commit()
        await db.refresh(req)
        return req

    async def list_privacy_requests(self, db: AsyncSession, customer_id: str) -> List[PrivacyRequest]:
        _ = await self._get_customer_or_404(db, customer_id)
        return await privacy_request_repository.list_by_customer(db, customer_id)

    async def review_privacy_request(self, db: AsyncSession, actor: User, request_id: str, payload) -> PrivacyRequest:
        req = await privacy_request_repository.get_by_id(db, request_id)
        if req is None:
            raise NotFoundException("Privacy request not found")

        current_status = req.status
        if payload.status not in self.VALID_PRIVACY_STATUS_TRANSITIONS.get(current_status, set()):
            raise ValidationException(f"Invalid privacy status transition: {current_status} -> {payload.status}")

        req.status = payload.status
        req.resolution_summary = payload.resolution_summary
        req.reviewed_by = actor.id
        req.reviewed_at = datetime.utcnow()
        if payload.status == "completed":
            req.completed_by = actor.id
            req.completed_at = datetime.utcnow()

        db.add(req)
        await self._append_privacy_event(
            db=db,
            privacy_request_id=req.id,
            event_type="reviewed",
            from_status=current_status,
            to_status=req.status,
            actor_user_id=actor.id,
            metadata={"resolution_summary": payload.resolution_summary},
        )
        await self._audit(
            db, actor.id, req.customer_id, "customer:privacy-request:review", f"request_id={req.id};status={req.status}"
        )
        await db.commit()
        await db.refresh(req)
        return req

    async def _get_customer_or_404(self, db: AsyncSession, customer_id: str) -> User:
        customer = await user_service.get_by_id(db=db, id=customer_id)
        if customer is None or customer.role != "customer" or customer.deleted_at is not None:
            raise NotFoundException("Customer not found")
        return customer

    async def _append_privacy_event(
        self,
        *,
        db: AsyncSession,
        privacy_request_id: str,
        event_type: str,
        from_status: str | None,
        to_status: str | None,
        actor_user_id: str | None,
        metadata: dict | None,
    ) -> None:
        db.add(
            PrivacyRequestEvent(
                privacy_request_id=privacy_request_id,
                event_type=event_type,
                from_status=from_status,
                to_status=to_status,
                actor_user_id=actor_user_id,
                metadata_json=metadata,
            )
        )

    async def _audit(self, db: AsyncSession, actor_user_id: str, target_user_id: str, action: str, details: str) -> None:
        db.add(
            StaffAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action=action,
                details=details,
            )
        )


admin_customer_service = AdminCustomerService()
