import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.commercial_audit_log import CommercialAuditLog
from app.models.promotion import Promotion
from app.models.promotion_redemption import PromotionRedemption
from app.models.user import User
from app.repositories.concrete.promotion_repository import promotion_repository
from app.repositories.concrete.service_offering_repository import service_offering_repository
from app.schemas.promotions import PromotionUpsertRequest


class PromotionService:
    async def create_promotion(self, db: AsyncSession, actor: User, payload: PromotionUpsertRequest) -> Promotion:
        await self._validate_payload(payload)
        if await promotion_repository.get_by_code(db, payload.code):
            raise ConflictException("Promotion code already exists")

        service_id = await self._resolve_service_id(db, payload.service_code)
        promo = Promotion(
            code=payload.code,
            promotion_type=payload.promotion_type,
            service_id=service_id,
            discount_percent=payload.discount_percent,
            discount_amount=payload.discount_amount,
            max_redemptions=payload.max_redemptions,
            per_user_limit=payload.per_user_limit,
            stack_rule=payload.stack_rule,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            active=payload.active,
        )
        db.add(promo)
        await db.flush()
        await self._audit(db, actor, promo.id, "create", before=None, after=promo.to_dict())
        await db.commit()
        await db.refresh(promo)
        return promo

    async def update_promotion(
        self, db: AsyncSession, actor: User, promotion_id: str, payload: PromotionUpsertRequest
    ) -> Promotion:
        await self._validate_payload(payload)
        promo = await promotion_repository.get_by_id(db, promotion_id)
        if promo is None:
            raise NotFoundException("Promotion not found")

        existing = await promotion_repository.get_by_code(db, payload.code)
        if existing and existing.id != promo.id:
            raise ConflictException("Promotion code already exists")

        before = promo.to_dict()
        promo.code = payload.code
        promo.promotion_type = payload.promotion_type
        promo.service_id = await self._resolve_service_id(db, payload.service_code)
        promo.discount_percent = payload.discount_percent
        promo.discount_amount = payload.discount_amount
        promo.max_redemptions = payload.max_redemptions
        promo.per_user_limit = payload.per_user_limit
        promo.stack_rule = payload.stack_rule
        promo.effective_from = payload.effective_from
        promo.effective_to = payload.effective_to
        promo.active = payload.active

        db.add(promo)
        await db.flush()
        await self._audit(db, actor, promo.id, "update", before=before, after=promo.to_dict())
        await db.commit()
        await db.refresh(promo)
        return promo

    async def list_promotions(self, db: AsyncSession, *, include_inactive: bool) -> List[Promotion]:
        stmt = select(Promotion).where(Promotion.deleted_at.is_(None))
        if not include_inactive:
            stmt = stmt.where(Promotion.active.is_(True))
        stmt = stmt.order_by(Promotion.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_promotion_by_id(self, db: AsyncSession, promotion_id: str) -> Promotion:
        promo = await promotion_repository.get_by_id(db, promotion_id)
        if promo is None:
            raise NotFoundException("Promotion not found")
        return promo

    async def deactivate_promotion(self, db: AsyncSession, actor: User, promotion_id: str) -> Promotion:
        promo = await promotion_repository.get_by_id(db, promotion_id)
        if promo is None:
            raise NotFoundException("Promotion not found")

        if not promo.active:
            return promo

        before = promo.to_dict()
        promo.active = False
        db.add(promo)
        await db.flush()
        await self._audit(db, actor, promo.id, "deactivate", before=before, after=promo.to_dict())
        await db.commit()
        await db.refresh(promo)
        return promo

    async def delete_promotion(self, db: AsyncSession, actor: User, promotion_id: str) -> None:
        promo = await promotion_repository.get_by_id(db, promotion_id)
        if promo is None:
            raise NotFoundException("Promotion not found")

        before = promo.to_dict()
        promo.deleted_at = datetime.utcnow()
        db.add(promo)
        await db.flush()
        await self._audit(db, actor, promo.id, "delete", before=before, after=None)
        await db.commit()

    async def get_performance(self, db: AsyncSession, *, code: Optional[str]) -> list[dict]:
        stmt = (
            select(
                Promotion.id.label("promotion_id"),
                Promotion.code.label("code"),
                func.count(PromotionRedemption.id).label("total_redemptions"),
                func.coalesce(
                    func.sum(case((PromotionRedemption.status == "consumed", 1), else_=0)),
                    0,
                ).label("consumed_redemptions"),
                func.coalesce(
                    func.sum(case((PromotionRedemption.status == "consumed", PromotionRedemption.redeemed_amount), else_=0)),
                    0,
                ).label("estimated_discount_cost"),
            )
            .select_from(Promotion)
            .outerjoin(
                PromotionRedemption,
                (PromotionRedemption.promotion_id == Promotion.id) & (PromotionRedemption.deleted_at.is_(None)),
            )
            .where(Promotion.deleted_at.is_(None))
            .group_by(Promotion.id, Promotion.code)
            .order_by(Promotion.code.asc())
        )
        if code:
            stmt = stmt.where(func.lower(Promotion.code) == code.lower())
        result = await db.execute(stmt)
        rows = result.mappings().all()
        return [
            {
                "promotion_id": r["promotion_id"],
                "code": r["code"],
                "total_redemptions": int(r["total_redemptions"] or 0),
                "consumed_redemptions": int(r["consumed_redemptions"] or 0),
                "gmv_with_promotion": 0,
                "estimated_discount_cost": int(r["estimated_discount_cost"] or 0),
            }
            for r in rows
        ]

    async def _resolve_service_id(self, db: AsyncSession, service_code: Optional[str]) -> Optional[str]:
        if not service_code:
            return None
        offering = await service_offering_repository.get_by_code(db, service_code)
        if offering is None:
            raise NotFoundException("Service offering not found")
        return offering.id

    async def _validate_payload(self, payload: PromotionUpsertRequest) -> None:
        if payload.effective_to is not None and payload.effective_to <= payload.effective_from:
            raise ValidationException("effective_to must be after effective_from")
        if payload.promotion_type == "percent" and payload.discount_percent is None:
            raise ValidationException("discount_percent is required for percent promotion")
        if payload.promotion_type == "fixed" and payload.discount_amount is None:
            raise ValidationException("discount_amount is required for fixed promotion")

    async def _audit(
        self,
        db: AsyncSession,
        actor: User,
        entity_id: str,
        action: str,
        *,
        before,
        after,
    ) -> None:
        db.add(
            CommercialAuditLog(
                actor_user_id=actor.id,
                entity_type="promotion",
                entity_id=entity_id,
                action=action,
                before=json.dumps(before, default=str) if before is not None else None,
                after=json.dumps(after, default=str) if after is not None else None,
            )
        )


promotion_service = PromotionService()
