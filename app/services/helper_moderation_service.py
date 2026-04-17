import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from app.models.helper_document import HelperDocument
from app.models.helper_document_type import HelperDocumentType
from app.models.helper_profile import HelperProfile
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User
from app.repositories.concrete.helper_document_repository import helper_document_repository
from app.repositories.concrete.helper_document_type_repository import helper_document_type_repository
from app.repositories.concrete.helper_profile_repository import helper_profile_repository
from app.services.user_service import user_service


class HelperModerationService:
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "application/pdf"}
    MAX_FILE_SIZE = 10 * 1024 * 1024
    PRESIGNED_TTL_SECONDS = 15 * 60

    async def ensure_helper_profile(self, db: AsyncSession, helper_user: User) -> HelperProfile:
        profile = await helper_profile_repository.get_by_user_id(db, helper_user.id)
        if profile:
            return profile
        display_name = helper_user.email or helper_user.phone or helper_user.id
        profile = HelperProfile(
            user_id=helper_user.id,
            display_name=display_name,
            skills=[],
            service_area={"city": "hanoi"},
            approval_status="pending",
        )
        db.add(profile)
        await db.flush()
        return profile

    async def list_helpers(self, db: AsyncSession, approval_status: Optional[str]) -> List[tuple[User, HelperProfile]]:
        profiles = await helper_profile_repository.list_by_status(db, approval_status)
        rows: List[tuple[User, HelperProfile]] = []
        for profile in profiles:
            helper = await user_service.get_by_id(db, id=profile.user_id)
            if helper and helper.role == "helper":
                rows.append((helper, profile))
        return rows

    async def get_helper_detail(self, db: AsyncSession, helper_id: str) -> tuple[User, HelperProfile]:
        helper = await user_service.get_by_id(db, id=helper_id)
        if helper is None or helper.role != "helper":
            raise NotFoundException("Helper not found")
        profile = await self.ensure_helper_profile(db, helper)
        await db.commit()
        await db.refresh(profile)
        return helper, profile

    async def moderate_status(self, db: AsyncSession, actor: User, helper_id: str, target_status: str, reason: Optional[str]) -> HelperProfile:
        helper, profile = await self.get_helper_detail(db, helper_id)
        before = profile.approval_status
        if before == target_status:
            raise ConflictException("Helper already in target moderation state")

        if target_status == "approved":
            profile.approval_status = "approved"
            profile.approved_at = datetime.utcnow()
            profile.approved_by = actor.id
            profile.suspension_reason_code = None
            helper.status = "active"
        elif target_status == "rejected":
            profile.approval_status = "rejected"
            profile.suspension_reason_code = reason
            helper.status = "inactive"
        elif target_status == "suspended":
            profile.approval_status = "suspended"
            profile.suspension_reason_code = reason
            helper.status = "suspended"
        elif target_status == "pending":
            profile.approval_status = "pending"
            profile.suspension_reason_code = None
            helper.status = "active"
        else:
            raise ValidationException("Invalid moderation status")

        db.add(profile)
        db.add(helper)
        await self._audit(db, actor.id, helper.id, f"helper:{target_status}", f"{before}->{target_status};reason={reason or ''}")
        await db.commit()
        await db.refresh(profile)
        return profile

    async def upsert_document_type(
        self, db: AsyncSession, actor: User, payload
    ) -> HelperDocumentType:
        doc_type = await helper_document_type_repository.get_by_code(db, payload.code)
        action = "kyc:doc-type:update"
        if doc_type is None:
            doc_type = HelperDocumentType(code=payload.code)
            action = "kyc:doc-type:create"
        doc_type.name = payload.name
        doc_type.required = payload.required
        doc_type.active = payload.active
        doc_type.sort_order = payload.sort_order
        db.add(doc_type)
        await db.flush()
        await self._audit(db, actor.id, doc_type.id, action, json.dumps(doc_type.to_dict(), default=str))
        await db.commit()
        await db.refresh(doc_type)
        return doc_type

    async def list_document_types(self, db: AsyncSession, include_inactive: bool) -> List[HelperDocumentType]:
        if include_inactive:
            return await helper_document_type_repository.get_all(db, include_deleted=False)
        return await helper_document_type_repository.list_active(db)

    async def create_upload_intent(self, db: AsyncSession, helper: User, payload):
        if helper.role != "helper":
            raise ForbiddenException("Helper role is required")
        if payload.mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValidationException("mime_type is not allowed")
        if payload.file_size_bytes > self.MAX_FILE_SIZE:
            raise ValidationException("file_size_bytes exceeds 10 MiB")
        doc_type = await helper_document_type_repository.get_by_code(db, payload.document_type)
        if doc_type is None or not doc_type.active:
            raise ValidationException("document_type is invalid or inactive")
        storage_ref = f"helpers/{helper.id}/documents/{uuid.uuid4()}-{payload.file_name}"
        upload_url = f"https://storage.local/upload/{storage_ref}?expires_in={self.PRESIGNED_TTL_SECONDS}"
        return {
            "upload_url": upload_url,
            "storage_ref": storage_ref,
            "expires_in_seconds": self.PRESIGNED_TTL_SECONDS,
            "required_headers": {"Content-Type": payload.mime_type},
        }

    async def submit_document(self, db: AsyncSession, helper: User, payload) -> HelperDocument:
        if helper.role != "helper":
            raise ForbiddenException("Helper role is required")
        if payload.mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValidationException("mime_type is not allowed")
        if payload.file_size_bytes > self.MAX_FILE_SIZE:
            raise ValidationException("file_size_bytes exceeds 10 MiB")

        doc_type = await helper_document_type_repository.get_by_code(db, payload.document_type)
        if doc_type is None or not doc_type.active:
            raise ValidationException("document_type is invalid or inactive")

        document = HelperDocument(
            helper_id=helper.id,
            document_type=payload.document_type,
            storage_ref=payload.storage_ref,
            mime_type=payload.mime_type,
            file_size_bytes=payload.file_size_bytes,
            status="pending_review",
        )
        db.add(document)
        await self._audit(db, helper.id, helper.id, "helper:kyc:submit", f"document_type={payload.document_type}")
        await db.commit()
        await db.refresh(document)
        return document

    async def list_own_documents(self, db: AsyncSession, helper: User) -> List[HelperDocument]:
        if helper.role != "helper":
            raise ForbiddenException("Helper role is required")
        return await helper_document_repository.list_by_helper(db, helper.id)

    async def list_review_queue(
        self, db: AsyncSession, status: Optional[str], document_type: Optional[str], helper_id: Optional[str]
    ) -> List[HelperDocument]:
        return await helper_document_repository.list_for_review_queue(
            db,
            status=status,
            document_type=document_type,
            helper_id=helper_id,
        )

    async def review_document(self, db: AsyncSession, actor: User, document_id: str, payload) -> HelperDocument:
        document = await helper_document_repository.get_by_id(db, document_id)
        if document is None:
            raise NotFoundException("Helper document not found")
        document.status = payload.status
        document.review_reason_code = payload.review_reason_code
        document.reviewed_by = actor.id
        document.reviewed_at = datetime.utcnow()
        db.add(document)
        await self._audit(
            db,
            actor.id,
            document.helper_id,
            "kyc:review",
            f"document_id={document.id};status={payload.status};reason={payload.review_reason_code or ''}",
        )
        await db.commit()
        await db.refresh(document)
        return document

    async def assert_helper_eligible_for_accept(self, db: AsyncSession, helper_id: str) -> None:
        helper = await user_service.get_by_id(db, id=helper_id)
        if helper is None or helper.role != "helper":
            raise ForbiddenException("Helper is not eligible to accept booking")
        profile = await helper_profile_repository.get_by_user_id(db, helper.id)
        if profile is None or profile.approval_status != "approved":
            raise ForbiddenException("Helper moderation status is not approved")

        required_types = await helper_document_type_repository.list_required_codes(db)
        if not required_types:
            return
        approved_types = await helper_document_repository.list_approved_types(db, helper.id)
        missing = [doc_type for doc_type in required_types if doc_type not in approved_types]
        if missing:
            raise ForbiddenException(f"Missing required approved KYC documents: {', '.join(missing)}")

    async def get_eligibility(self, db: AsyncSession, helper_id: str) -> dict:
        required_types = await helper_document_type_repository.list_required_codes(db)
        approved_types = await helper_document_repository.list_approved_types(db, helper_id)
        missing = [doc_type for doc_type in required_types if doc_type not in approved_types]
        profile = await helper_profile_repository.get_by_user_id(db, helper_id)
        if profile is None or profile.approval_status != "approved":
            return {
                "eligible": False,
                "reason_code": "helper_not_approved",
                "missing_required_document_types": missing,
            }
        if missing:
            return {
                "eligible": False,
                "reason_code": "missing_required_kyc",
                "missing_required_document_types": missing,
            }
        return {"eligible": True, "reason_code": None, "missing_required_document_types": []}

    async def _audit(self, db: AsyncSession, actor_user_id: str, target_user_id: str, action: str, details: str) -> None:
        db.add(
            StaffAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action=action,
                details=details,
            )
        )


helper_moderation_service = HelperModerationService()
