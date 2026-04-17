from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import User
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.promotions import PromotionPerformanceResponse, PromotionResponse, PromotionUpsertRequest
from app.services.promotion_service import promotion_service
from app.utils.auth import require_permission

router = APIRouter()


def _to_response(p) -> PromotionResponse:
    return PromotionResponse(
        id=p.id,
        code=p.code,
        promotion_type=p.promotion_type,
        service_id=p.service_id,
        discount_percent=float(p.discount_percent) if p.discount_percent is not None else None,
        discount_amount=int(p.discount_amount) if p.discount_amount is not None else None,
        max_redemptions=p.max_redemptions,
        per_user_limit=p.per_user_limit,
        stack_rule=p.stack_rule,
        effective_from=p.effective_from,
        effective_to=p.effective_to,
        active=bool(p.active),
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@router.post("/promotions", response_model=SuccessResponse[PromotionResponse])  # type: ignore[misc]
async def create_promotion(
    payload: PromotionUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[PromotionResponse]:
    promo = await promotion_service.create_promotion(db=db, actor=current_user, payload=payload)
    return ResponseBuilder.created("Promotion created", _to_response(promo))


@router.put("/promotions/{promotion_id}", response_model=SuccessResponse[PromotionResponse])  # type: ignore[misc]
async def update_promotion(
    promotion_id: str,
    payload: PromotionUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[PromotionResponse]:
    promo = await promotion_service.update_promotion(db=db, actor=current_user, promotion_id=promotion_id, payload=payload)
    return ResponseBuilder.updated("Promotion updated", _to_response(promo))


@router.get("/promotions", response_model=SuccessResponse[List[PromotionResponse]])  # type: ignore[misc]
async def list_promotions(
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[List[PromotionResponse]]:
    promotions = await promotion_service.list_promotions(db=db, include_inactive=include_inactive)
    return ResponseBuilder.success("Promotions retrieved", [_to_response(p) for p in promotions])


@router.get("/promotions/performance", response_model=SuccessResponse[List[PromotionPerformanceResponse]])  # type: ignore[misc]
async def promotion_performance(
    code: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[List[PromotionPerformanceResponse]]:
    rows = await promotion_service.get_performance(db=db, code=code)
    return ResponseBuilder.success("Promotion performance retrieved", [PromotionPerformanceResponse(**r) for r in rows])


@router.get("/promotions/{promotion_id}", response_model=SuccessResponse[PromotionResponse])  # type: ignore[misc]
async def get_promotion(
    promotion_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[PromotionResponse]:
    promo = await promotion_service.get_promotion_by_id(db=db, promotion_id=promotion_id)
    return ResponseBuilder.success("Promotion retrieved", _to_response(promo))


@router.patch("/promotions/{promotion_id}/deactivate", response_model=SuccessResponse[PromotionResponse])  # type: ignore[misc]
async def deactivate_promotion(
    promotion_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[PromotionResponse]:
    promo = await promotion_service.deactivate_promotion(db=db, actor=current_user, promotion_id=promotion_id)
    return ResponseBuilder.updated("Promotion deactivated", _to_response(promo))


@router.delete("/promotions/{promotion_id}", response_model=SuccessResponse[None])  # type: ignore[misc]
async def delete_promotion(
    promotion_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("pricing:write")),
) -> SuccessResponse[None]:
    await promotion_service.delete_promotion(db=db, actor=current_user, promotion_id=promotion_id)
    return ResponseBuilder.deleted("Promotion deleted")
