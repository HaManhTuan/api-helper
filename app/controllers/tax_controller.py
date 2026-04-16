from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.tax import TaxConfigResponse, TaxConfigUpsertRequest, TaxRuleResponse, TaxRuleUpsertRequest
from app.services.tax_service import tax_service
from app.utils.auth import require_permission

router = APIRouter()


def _tax_rule_to_response(r) -> TaxRuleResponse:
    return TaxRuleResponse(
        id=r.id,
        service_offering_id=r.service_offering_id,
        vat_rate=float(r.vat_rate),
        price_display_mode=r.price_display_mode,
        commission_base=r.commission_base,
        rounding_mode=r.rounding_mode,
        effective_from=r.effective_from,
        effective_to=r.effective_to,
        priority=int(r.priority),
        active=bool(r.active),
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.post("/tax/rules", response_model=SuccessResponse[TaxRuleResponse])  # type: ignore[misc]
async def create_tax_rule(
    payload: TaxRuleUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[TaxRuleResponse]:
    rule = await tax_service.upsert_tax_rule(db=db, actor=current_user, payload=payload)
    return ResponseBuilder.created("Tax rule created", _tax_rule_to_response(rule))


@router.get("/tax/config", response_model=SuccessResponse[TaxConfigResponse])  # type: ignore[misc]
async def get_tax_config(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[TaxConfigResponse]:
    cfg = await tax_service.get_tax_config(db=db)
    return ResponseBuilder.success("Tax config retrieved", TaxConfigResponse(platform_tax_id=cfg.value.get("platform_tax_id")))


@router.put("/tax/config", response_model=SuccessResponse[TaxConfigResponse])  # type: ignore[misc]
async def update_tax_config(
    payload: TaxConfigUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[TaxConfigResponse]:
    cfg = await tax_service.upsert_tax_config(db=db, actor=current_user, payload=payload)
    return ResponseBuilder.updated("Tax config updated", TaxConfigResponse(platform_tax_id=cfg.value.get("platform_tax_id")))

