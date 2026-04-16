import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException, ValidationException
from app.models.commercial_audit_log import CommercialAuditLog
from app.models.tax_config import TaxConfig
from app.models.tax_rule import TaxRule
from app.models.user import User
from app.repositories.concrete.service_offering_repository import service_offering_repository
from app.repositories.concrete.tax_rule_repository import tax_rule_repository


class TaxService:
    async def upsert_tax_rule(self, db: AsyncSession, actor: User, payload) -> TaxRule:
        service_offering_id: Optional[str] = None
        if payload.service_code:
            offering = await service_offering_repository.get_by_code(db, payload.service_code)
            if offering is None:
                raise NotFoundException("Service offering not found")
            service_offering_id = offering.id

        if payload.effective_to is not None and payload.effective_to <= payload.effective_from:
            raise ValidationException("effective_to must be after effective_from")

        if payload.price_display_mode not in {"inclusive", "exclusive"}:
            raise ValidationException("price_display_mode must be inclusive|exclusive")

        if payload.commission_base not in {"before_vat", "after_vat"}:
            raise ValidationException("commission_base must be before_vat|after_vat")

        rule = TaxRule(
            service_offering_id=service_offering_id,
            vat_rate=payload.vat_rate,
            price_display_mode=payload.price_display_mode,
            commission_base=payload.commission_base,
            rounding_mode=payload.rounding_mode,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            priority=payload.priority,
            active=payload.active,
        )
        db.add(rule)
        await db.flush()
        await self._audit(db, actor, "tax_rule", rule.id, "create", before=None, after=rule.to_dict())
        await db.commit()
        await db.refresh(rule)
        return rule

    async def resolve_tax_rule(self, db: AsyncSession, *, service_offering_id: str, at: datetime) -> Optional[TaxRule]:
        return await tax_rule_repository.resolve_active(db, service_offering_id=service_offering_id, at=at)

    async def upsert_tax_config(self, db: AsyncSession, actor: User, payload) -> TaxConfig:
        key = "platform"
        result = await db.execute(select(TaxConfig).where(TaxConfig.key == key, TaxConfig.deleted_at.is_(None)))
        cfg = result.scalar_one_or_none()
        before = cfg.to_dict() if cfg else None

        if cfg is None:
            cfg = TaxConfig(key=key, value={})
            db.add(cfg)
            await db.flush()

        if payload.platform_tax_id is not None:
            cfg.value["platform_tax_id"] = payload.platform_tax_id

        db.add(cfg)
        await db.flush()
        await self._audit(db, actor, "tax_config", cfg.id, "update", before=before, after=cfg.to_dict())
        await db.commit()
        await db.refresh(cfg)
        return cfg

    async def get_tax_config(self, db: AsyncSession) -> TaxConfig:
        key = "platform"
        result = await db.execute(select(TaxConfig).where(TaxConfig.key == key, TaxConfig.deleted_at.is_(None)))
        cfg = result.scalar_one_or_none()
        if cfg is None:
            cfg = TaxConfig(key=key, value={})
            db.add(cfg)
            await db.commit()
            await db.refresh(cfg)
        return cfg

    def compute_tax_breakdown(
        self, *, gross_or_net_amount: int, vat_rate: Decimal, display_mode: str
    ) -> tuple[int, int, int]:
        """
        Returns (subtotal_before_tax, tax_amount, total_after_tax).

        - If display_mode == inclusive: input is total_after_tax, we back-calc net + tax.
        - If display_mode == exclusive: input is subtotal_before_tax, we calc tax + gross.
        """
        if vat_rate <= 0:
            if display_mode == "inclusive":
                return gross_or_net_amount, 0, gross_or_net_amount
            return gross_or_net_amount, 0, gross_or_net_amount

        rate = vat_rate / Decimal(100)
        amount = Decimal(gross_or_net_amount)

        if display_mode == "inclusive":
            net = (amount / (Decimal(1) + rate)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            tax = (amount - net).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            return int(net), int(tax), int(amount)

        # exclusive
        tax = (amount * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        gross = (amount + tax).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return int(amount), int(tax), int(gross)

    async def _audit(self, db: AsyncSession, actor: User, entity_type: str, entity_id: str, action: str, *, before, after) -> None:
        db.add(
            CommercialAuditLog(
                actor_user_id=actor.id,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                before=json.dumps(before, default=str) if before is not None else None,
                after=json.dumps(after, default=str) if after is not None else None,
            )
        )


tax_service = TaxService()

