from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException
from app.models.privacy_request import PrivacyRequest
from app.models.privacy_request_event import PrivacyRequestEvent
from app.models.user import User
from app.repositories.concrete.privacy_request_repository import privacy_request_repository


class CustomerPrivacyService:
    async def create_request(self, db: AsyncSession, customer: User, payload) -> PrivacyRequest:
        req = PrivacyRequest(
            customer_id=customer.id,
            request_type=payload.request_type,
            status="submitted",
            legal_basis=payload.legal_basis,
            requested_payload=payload.requested_payload,
        )
        db.add(req)
        await db.flush()
        db.add(
            PrivacyRequestEvent(
                privacy_request_id=req.id,
                event_type="submitted",
                from_status=None,
                to_status=req.status,
                actor_user_id=customer.id,
                metadata_json={"request_type": payload.request_type},
            )
        )
        await db.commit()
        await db.refresh(req)
        return req

    async def list_own_requests(self, db: AsyncSession, customer: User) -> List[PrivacyRequest]:
        return await privacy_request_repository.list_by_customer(db, customer.id)

    async def get_own_request(self, db: AsyncSession, customer: User, request_id: str) -> PrivacyRequest:
        req = await privacy_request_repository.get_by_id_and_customer(db, request_id, customer.id)
        if req is None:
            raise NotFoundException("Privacy request not found")
        return req

    def build_download_url(self, req: PrivacyRequest) -> str | None:
        if req.request_type == "export" and req.status in {"completed", "ready"} and req.export_job_id:
            return f"/api/v1/customer/privacy-requests/{req.id}/download?token={req.export_job_id}"
        return None


customer_privacy_service = CustomerPrivacyService()
