from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.exceptions import ForbiddenException
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.helpers import (
    HelperDocumentResponse,
    HelperDocumentSubmitRequest,
    HelperDocumentUploadIntentRequest,
    HelperDocumentUploadIntentResponse,
)
from app.services.helper_moderation_service import helper_moderation_service
from app.utils.auth import get_current_user

router = APIRouter()


def _document_response(doc) -> HelperDocumentResponse:
    return HelperDocumentResponse(
        id=doc.id,
        helper_id=doc.helper_id,
        document_type=doc.document_type,
        storage_ref=doc.storage_ref,
        mime_type=doc.mime_type,
        file_size_bytes=int(doc.file_size_bytes),
        status=doc.status,
        review_reason_code=doc.review_reason_code,
        reviewed_by=doc.reviewed_by,
        reviewed_at=doc.reviewed_at,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


def _require_helper(user: User) -> None:
    if user.role != "helper":
        raise ForbiddenException("Helper role is required")


@router.post("/helper/documents/upload-intent", response_model=SuccessResponse[HelperDocumentUploadIntentResponse])  # type: ignore[misc]
async def create_upload_intent(
    payload: HelperDocumentUploadIntentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[HelperDocumentUploadIntentResponse]:
    _require_helper(current_user)
    intent = await helper_moderation_service.create_upload_intent(db, current_user, payload)
    return ResponseBuilder.success("Upload intent created", HelperDocumentUploadIntentResponse(**intent))


@router.post("/helper/documents", response_model=SuccessResponse[HelperDocumentResponse])  # type: ignore[misc]
async def submit_helper_document(
    payload: HelperDocumentSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[HelperDocumentResponse]:
    _require_helper(current_user)
    doc = await helper_moderation_service.submit_document(db, current_user, payload)
    return ResponseBuilder.created("Helper document submitted", _document_response(doc))


@router.get("/helper/documents", response_model=SuccessResponse[List[HelperDocumentResponse]])  # type: ignore[misc]
async def list_own_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[List[HelperDocumentResponse]]:
    _require_helper(current_user)
    docs = await helper_moderation_service.list_own_documents(db, current_user)
    return ResponseBuilder.success("Helper documents retrieved", [_document_response(d) for d in docs])
