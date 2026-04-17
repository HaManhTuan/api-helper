from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.insurance import (
    InsuranceClaimCreateRequest,
    InsuranceClaimResponse,
    InsuranceClaimUpdateRequest,
    InsuranceEnrollmentResponse,
    InsuranceEnrollmentUpsertRequest,
    InsuranceProductResponse,
    InsuranceProductUpsertRequest,
    ServiceInsuranceRuleResponse,
    ServiceInsuranceRuleUpdateRequest,
)
from app.services.insurance_risk_service import insurance_risk_service
from app.utils.auth import require_permission

router = APIRouter()


def _product_response(item) -> InsuranceProductResponse:
    return InsuranceProductResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        coverage_summary=item.coverage_summary,
        premium_model=item.premium_model,
        eligibility_rule=item.eligibility_rule,
        active=bool(item.active),
        valid_from=item.valid_from,
        valid_to=item.valid_to,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _enrollment_response(item) -> InsuranceEnrollmentResponse:
    return InsuranceEnrollmentResponse(
        id=item.id,
        helper_id=item.helper_id,
        product_id=item.product_id,
        status=item.status,
        effective_from=item.effective_from,
        effective_to=item.effective_to,
        notes=item.notes,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _claim_response(item) -> InsuranceClaimResponse:
    return InsuranceClaimResponse(
        id=item.id,
        booking_id=item.booking_id,
        reporter_role=item.reporter_role,
        description=item.description,
        severity=item.severity,
        status=item.status,
        resolution_notes=item.resolution_notes,
        payout_amount=item.payout_amount,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("/insurance/products", response_model=SuccessResponse[InsuranceProductResponse])  # type: ignore[misc]
async def create_product(
    payload: InsuranceProductUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("insurance:manage")),
) -> SuccessResponse[InsuranceProductResponse]:
    row = await insurance_risk_service.upsert_product(db, current_user, None, payload)
    return ResponseBuilder.created("Insurance product created", _product_response(row))


@router.put("/insurance/products/{product_id}", response_model=SuccessResponse[InsuranceProductResponse])  # type: ignore[misc]
async def update_product(
    product_id: str,
    payload: InsuranceProductUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("insurance:manage")),
) -> SuccessResponse[InsuranceProductResponse]:
    row = await insurance_risk_service.upsert_product(db, current_user, product_id, payload)
    return ResponseBuilder.updated("Insurance product updated", _product_response(row))


@router.get("/insurance/products", response_model=SuccessResponse[List[InsuranceProductResponse]])  # type: ignore[misc]
async def list_products(
    active: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("insurance:read")),
) -> SuccessResponse[List[InsuranceProductResponse]]:
    rows = await insurance_risk_service.list_products(db, active=active)
    return ResponseBuilder.success("Insurance products retrieved", [_product_response(item) for item in rows])


@router.post("/insurance/enrollments", response_model=SuccessResponse[InsuranceEnrollmentResponse])  # type: ignore[misc]
async def upsert_enrollment(
    payload: InsuranceEnrollmentUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("insurance:manage")),
) -> SuccessResponse[InsuranceEnrollmentResponse]:
    row = await insurance_risk_service.upsert_enrollment(db, current_user, None, payload)
    return ResponseBuilder.created("Insurance enrollment upserted", _enrollment_response(row))


@router.put("/insurance/enrollments/{enrollment_id}", response_model=SuccessResponse[InsuranceEnrollmentResponse])  # type: ignore[misc]
async def update_enrollment(
    enrollment_id: str,
    payload: InsuranceEnrollmentUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("insurance:manage")),
) -> SuccessResponse[InsuranceEnrollmentResponse]:
    row = await insurance_risk_service.upsert_enrollment(db, current_user, enrollment_id, payload)
    return ResponseBuilder.updated("Insurance enrollment updated", _enrollment_response(row))


@router.get("/insurance/enrollments", response_model=SuccessResponse[List[InsuranceEnrollmentResponse]])  # type: ignore[misc]
async def list_enrollments(
    helper_id: Optional[str] = Query(default=None),
    product_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("insurance:read")),
) -> SuccessResponse[List[InsuranceEnrollmentResponse]]:
    rows = await insurance_risk_service.list_enrollments(db, helper_id=helper_id, product_id=product_id, status=status)
    return ResponseBuilder.success("Insurance enrollments retrieved", [_enrollment_response(item) for item in rows])


@router.post("/insurance/claims", response_model=SuccessResponse[InsuranceClaimResponse])  # type: ignore[misc]
async def create_claim(
    payload: InsuranceClaimCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("insurance:manage")),
) -> SuccessResponse[InsuranceClaimResponse]:
    row = await insurance_risk_service.create_claim(db, current_user, payload)
    return ResponseBuilder.created("Insurance claim created", _claim_response(row))


@router.put("/insurance/claims/{claim_id}", response_model=SuccessResponse[InsuranceClaimResponse])  # type: ignore[misc]
async def update_claim(
    claim_id: str,
    payload: InsuranceClaimUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("insurance:manage")),
) -> SuccessResponse[InsuranceClaimResponse]:
    row = await insurance_risk_service.update_claim(db, current_user, claim_id, payload)
    return ResponseBuilder.updated("Insurance claim updated", _claim_response(row))


@router.get("/insurance/claims", response_model=SuccessResponse[List[InsuranceClaimResponse]])  # type: ignore[misc]
async def list_claims(
    status: Optional[str] = Query(default=None),
    booking_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("insurance:read")),
) -> SuccessResponse[List[InsuranceClaimResponse]]:
    rows = await insurance_risk_service.list_claims(db, status=status, booking_id=booking_id)
    return ResponseBuilder.success("Insurance claims retrieved", [_claim_response(item) for item in rows])


@router.put("/insurance/services/{service_id}/rule", response_model=SuccessResponse[ServiceInsuranceRuleResponse])  # type: ignore[misc]
async def update_service_rule(
    service_id: str,
    payload: ServiceInsuranceRuleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("insurance:manage")),
) -> SuccessResponse[ServiceInsuranceRuleResponse]:
    service = await insurance_risk_service.update_service_rule(db, current_user, service_id, payload)
    return ResponseBuilder.updated(
        "Service insurance rule updated",
        ServiceInsuranceRuleResponse(
            service_id=service.id,
            insurance_required=bool(service.insurance_required),
            insurance_enforcement=service.insurance_enforcement,
        ),
    )
