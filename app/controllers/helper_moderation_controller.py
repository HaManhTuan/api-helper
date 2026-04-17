from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.helpers import (
    HelperDocumentResponse,
    HelperDocumentReviewRequest,
    HelperDocumentTypeResponse,
    HelperDocumentTypeUpsertRequest,
    HelperEligibilityResponse,
    HelperModerationActionRequest,
    HelperModerationDetailResponse,
    HelperProfileResponse,
)
from app.services.helper_moderation_service import helper_moderation_service
from app.utils.auth import require_permission

router = APIRouter()


def _profile_response(profile) -> HelperProfileResponse:
    return HelperProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        display_name=profile.display_name,
        skills=profile.skills or [],
        service_area=profile.service_area or {},
        approval_status=profile.approval_status,
        suspension_reason_code=profile.suspension_reason_code,
        aggregate_rating=float(profile.aggregate_rating),
        ratings_count=int(profile.ratings_count),
        approved_at=profile.approved_at,
        approved_by=profile.approved_by,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


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


def _doc_type_response(doc_type) -> HelperDocumentTypeResponse:
    return HelperDocumentTypeResponse(
        id=doc_type.id,
        code=doc_type.code,
        name=doc_type.name,
        required=bool(doc_type.required),
        active=bool(doc_type.active),
        sort_order=int(doc_type.sort_order),
    )


@router.get("/helpers", response_model=SuccessResponse[List[HelperModerationDetailResponse]])  # type: ignore[misc]
async def list_helpers(
    approval_status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("helpers:moderate")),
) -> SuccessResponse[List[HelperModerationDetailResponse]]:
    rows = await helper_moderation_service.list_helpers(db, approval_status)
    data = [
        HelperModerationDetailResponse(
            helper_id=user.id,
            role=user.role,
            account_status=user.status,
            email=user.email,
            phone=user.phone,
            profile=_profile_response(profile),
        )
        for user, profile in rows
    ]
    return ResponseBuilder.success("Helpers retrieved", data)


@router.get("/helpers/{helper_id}", response_model=SuccessResponse[HelperModerationDetailResponse])  # type: ignore[misc]
async def get_helper_detail(
    helper_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("helpers:moderate")),
) -> SuccessResponse[HelperModerationDetailResponse]:
    user, profile = await helper_moderation_service.get_helper_detail(db, helper_id)
    return ResponseBuilder.success(
        "Helper detail retrieved",
        HelperModerationDetailResponse(
            helper_id=user.id,
            role=user.role,
            account_status=user.status,
            email=user.email,
            phone=user.phone,
            profile=_profile_response(profile),
        ),
    )


@router.post("/helpers/{helper_id}/approve", response_model=SuccessResponse[HelperProfileResponse])  # type: ignore[misc]
async def approve_helper(
    helper_id: str,
    payload: HelperModerationActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("helpers:moderate")),
) -> SuccessResponse[HelperProfileResponse]:
    profile = await helper_moderation_service.moderate_status(db, current_user, helper_id, "approved", payload.reason_code)
    return ResponseBuilder.updated("Helper approved", _profile_response(profile))


@router.post("/helpers/{helper_id}/reject", response_model=SuccessResponse[HelperProfileResponse])  # type: ignore[misc]
async def reject_helper(
    helper_id: str,
    payload: HelperModerationActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("helpers:moderate")),
) -> SuccessResponse[HelperProfileResponse]:
    profile = await helper_moderation_service.moderate_status(db, current_user, helper_id, "rejected", payload.reason_code)
    return ResponseBuilder.updated("Helper rejected", _profile_response(profile))


@router.post("/helpers/{helper_id}/suspend", response_model=SuccessResponse[HelperProfileResponse])  # type: ignore[misc]
async def suspend_helper(
    helper_id: str,
    payload: HelperModerationActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("helpers:moderate")),
) -> SuccessResponse[HelperProfileResponse]:
    profile = await helper_moderation_service.moderate_status(db, current_user, helper_id, "suspended", payload.reason_code)
    return ResponseBuilder.updated("Helper suspended", _profile_response(profile))


@router.post("/helpers/{helper_id}/reinstate", response_model=SuccessResponse[HelperProfileResponse])  # type: ignore[misc]
async def reinstate_helper(
    helper_id: str,
    payload: HelperModerationActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("helpers:moderate")),
) -> SuccessResponse[HelperProfileResponse]:
    profile = await helper_moderation_service.moderate_status(db, current_user, helper_id, "approved", payload.reason_code)
    return ResponseBuilder.updated("Helper reinstated", _profile_response(profile))


@router.get("/helpers/{helper_id}/eligibility", response_model=SuccessResponse[HelperEligibilityResponse])  # type: ignore[misc]
async def helper_eligibility(
    helper_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("helpers:moderate")),
) -> SuccessResponse[HelperEligibilityResponse]:
    return ResponseBuilder.success(
        "Helper eligibility checked",
        HelperEligibilityResponse(**(await helper_moderation_service.get_eligibility(db, helper_id))),
    )


@router.post("/helpers/document-types", response_model=SuccessResponse[HelperDocumentTypeResponse])  # type: ignore[misc]
async def upsert_document_type(
    payload: HelperDocumentTypeUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("kyc:review")),
) -> SuccessResponse[HelperDocumentTypeResponse]:
    doc_type = await helper_moderation_service.upsert_document_type(db, current_user, payload)
    return ResponseBuilder.created("Helper document type upserted", _doc_type_response(doc_type))


@router.get("/helpers/document-types", response_model=SuccessResponse[List[HelperDocumentTypeResponse]])  # type: ignore[misc]
async def list_document_types(
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("kyc:review")),
) -> SuccessResponse[List[HelperDocumentTypeResponse]]:
    rows = await helper_moderation_service.list_document_types(db, include_inactive)
    return ResponseBuilder.success("Helper document types retrieved", [_doc_type_response(x) for x in rows])


@router.get("/helpers/documents", response_model=SuccessResponse[List[HelperDocumentResponse]])  # type: ignore[misc]
async def list_helper_documents_for_review(
    status: Optional[str] = Query(default=None),
    document_type: Optional[str] = Query(default=None),
    helper_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("kyc:review")),
) -> SuccessResponse[List[HelperDocumentResponse]]:
    docs = await helper_moderation_service.list_review_queue(
        db,
        status=status,
        document_type=document_type,
        helper_id=helper_id,
    )
    return ResponseBuilder.success("Helper documents retrieved", [_document_response(d) for d in docs])


@router.put("/helpers/documents/{document_id}/review", response_model=SuccessResponse[HelperDocumentResponse])  # type: ignore[misc]
async def review_helper_document(
    document_id: str,
    payload: HelperDocumentReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("kyc:review")),
) -> SuccessResponse[HelperDocumentResponse]:
    doc = await helper_moderation_service.review_document(db, current_user, document_id, payload)
    return ResponseBuilder.updated("Helper document reviewed", _document_response(doc))
