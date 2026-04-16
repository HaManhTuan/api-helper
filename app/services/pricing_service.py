import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.booking_financial_snapshot import BookingFinancialSnapshot
from app.models.commercial_audit_log import CommercialAuditLog
from app.models.commission_rule import CommissionRule
from app.models.price_book_entry import PriceBookEntry
from app.models.service_offering import ServiceOffering
from app.models.user import User
from app.repositories.concrete.commission_rule_repository import commission_rule_repository
from app.repositories.concrete.price_book_entry_repository import price_book_entry_repository
from app.repositories.concrete.service_offering_repository import service_offering_repository
from app.schemas.pricing import BookingSnapshotComputeRequest, CommissionRuleUpsertRequest, PriceBookEntryUpsertRequest
from app.services.tax_service import tax_service


class PricingService:
    async def create_service_offering(self, db: AsyncSession, actor: User, payload) -> ServiceOffering:
        existing = await service_offering_repository.get_by_code(db, payload.code)
        if existing:
            raise ConflictException("Service offering code already exists")

        offering = ServiceOffering(
            code=payload.code,
            name=payload.name,
            description=payload.description,
            unit=payload.unit,
            active=payload.active,
            tags=payload.tags,
            meta=payload.metadata,
        )
        db.add(offering)
        await db.flush()
        await self._audit(db, actor, "service_offering", offering.id, "create", before=None, after=offering.to_dict())
        await db.commit()
        await db.refresh(offering)
        return offering

    async def update_service_offering(self, db: AsyncSession, actor: User, offering_id: str, payload) -> ServiceOffering:
        offering = await service_offering_repository.get_by_id(db, offering_id)
        if offering is None:
            raise NotFoundException("Service offering not found")

        before = offering.to_dict()
        for field in ["name", "description", "unit", "active", "tags"]:
            value = getattr(payload, field)
            if value is not None:
                setattr(offering, field, value)

        if payload.metadata is not None:
            offering.meta = payload.metadata

        db.add(offering)
        await db.flush()
        await self._audit(db, actor, "service_offering", offering.id, "update", before=before, after=offering.to_dict())
        await db.commit()
        await db.refresh(offering)
        return offering

    async def list_service_offerings(self, db: AsyncSession, *, include_inactive: bool) -> List[ServiceOffering]:
        stmt = select(ServiceOffering).where(ServiceOffering.deleted_at.is_(None))
        if not include_inactive:
            stmt = stmt.where(ServiceOffering.active.is_(True))
        stmt = stmt.order_by(ServiceOffering.code.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def upsert_price_book_entry(
        self, db: AsyncSession, actor: User, payload: PriceBookEntryUpsertRequest
    ) -> PriceBookEntry:
        offering = await service_offering_repository.get_by_code(db, payload.service_code)
        if offering is None:
            raise NotFoundException("Service offering not found")

        if payload.effective_to is not None and payload.effective_to <= payload.effective_from:
            raise ValidationException("effective_to must be after effective_from")

        if payload.customer_price < 0 or payload.reference_cost < 0:
            raise ValidationException("Price and reference cost must be non-negative")

        entry = PriceBookEntry(
            service_offering_id=offering.id,
            variant_code=payload.variant_code,
            zone_code=payload.zone_code,
            currency=payload.currency,
            customer_price=payload.customer_price,
            reference_cost=payload.reference_cost,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            priority=payload.priority,
            active=payload.active,
        )
        db.add(entry)
        await db.flush()
        await self._audit(db, actor, "price_book_entry", entry.id, "create", before=None, after=entry.to_dict())
        await db.commit()
        await db.refresh(entry)
        return entry

    async def list_price_book_entries(self, db: AsyncSession, service_code: str) -> List[PriceBookEntry]:
        offering = await service_offering_repository.get_by_code(db, service_code)
        if offering is None:
            raise NotFoundException("Service offering not found")
        return await price_book_entry_repository.list_for_service(db, offering.id)

    async def upsert_commission_rule(
        self, db: AsyncSession, actor: User, payload: CommissionRuleUpsertRequest
    ) -> CommissionRule:
        service_offering_id: Optional[str] = None
        if payload.service_code:
            offering = await service_offering_repository.get_by_code(db, payload.service_code)
            if offering is None:
                raise NotFoundException("Service offering not found")
            service_offering_id = offering.id

        if payload.effective_to is not None and payload.effective_to <= payload.effective_from:
            raise ValidationException("effective_to must be after effective_from")

        if payload.helper_percent + payload.platform_percent > 100.0:
            raise ValidationException("helper_percent + platform_percent must be <= 100")

        rule = CommissionRule(
            service_offering_id=service_offering_id,
            helper_percent=payload.helper_percent,
            platform_percent=payload.platform_percent,
            fixed_platform_fee=payload.fixed_platform_fee,
            fixed_helper_fee=payload.fixed_helper_fee,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            priority=payload.priority,
            active=payload.active,
        )
        db.add(rule)
        await db.flush()
        await self._audit(db, actor, "commission_rule", rule.id, "create", before=None, after=rule.to_dict())
        await db.commit()
        await db.refresh(rule)
        return rule

    async def list_commission_rules(self, db: AsyncSession, service_code: Optional[str]) -> List[CommissionRule]:
        service_offering_id: Optional[str] = None
        if service_code:
            offering = await service_offering_repository.get_by_code(db, service_code)
            if offering is None:
                raise NotFoundException("Service offering not found")
            service_offering_id = offering.id
        return await commission_rule_repository.list_for_service(db, service_offering_id)

    async def compute_and_persist_snapshot(
        self, db: AsyncSession, actor: User, payload: BookingSnapshotComputeRequest
    ) -> BookingFinancialSnapshot:
        if not payload.line_items:
            raise ValidationException("line_items is required")

        computed_at = payload.at
        currency = "VND"

        line_breakdowns = []
        customer_total = 0
        subtotal_before_tax_total = 0
        tax_total = 0
        helper_total = 0
        platform_total = 0

        applied_price_entry_id: Optional[str] = None
        applied_commission_rule_id: Optional[str] = None

        for item in payload.line_items:
            offering = await service_offering_repository.get_by_code(db, item.service_code)
            if offering is None or not offering.active:
                raise ValidationException(f"Service offering not available: {item.service_code}")

            price_entry = await price_book_entry_repository.resolve_active(
                db,
                service_offering_id=offering.id,
                at=computed_at,
                zone_code=item.zone_code,
                variant_code=item.variant_code,
            )
            if price_entry is None:
                raise NotFoundException(f"No active price for service: {item.service_code}")

            rule = await commission_rule_repository.resolve_active(db, service_offering_id=offering.id, at=computed_at)
            if rule is None:
                raise NotFoundException("No commission rule configured (default or service-specific)")

            unit_price = int(price_entry.customer_price)
            raw_line_amount = unit_price * int(item.quantity)

            tax_rule = await tax_service.resolve_tax_rule(db=db, service_offering_id=offering.id, at=computed_at)
            vat_rate = Decimal(str(tax_rule.vat_rate)) if tax_rule else Decimal("0")
            display_mode = tax_rule.price_display_mode if tax_rule else "inclusive"
            commission_base = tax_rule.commission_base if tax_rule else "before_vat"

            subtotal_before_tax, line_tax, line_total = tax_service.compute_tax_breakdown(
                gross_or_net_amount=raw_line_amount,
                vat_rate=vat_rate,
                display_mode=display_mode,
            )

            commission_amount = subtotal_before_tax if commission_base == "before_vat" else line_total

            helper_earnings, platform_fee = self._split_commission(
                base_amount=commission_amount,
                helper_percent=Decimal(str(rule.helper_percent)),
                platform_percent=Decimal(str(rule.platform_percent)),
                fixed_helper_fee=int(rule.fixed_helper_fee),
                fixed_platform_fee=int(rule.fixed_platform_fee),
            )

            customer_total += line_total
            subtotal_before_tax_total += subtotal_before_tax
            tax_total += line_tax
            helper_total += helper_earnings
            platform_total += platform_fee

            applied_price_entry_id = applied_price_entry_id or price_entry.id
            applied_commission_rule_id = applied_commission_rule_id or rule.id

            line_breakdowns.append(
                {
                    "service_code": item.service_code,
                    "quantity": int(item.quantity),
                    "unit_price": unit_price,
                    "subtotal_before_tax": subtotal_before_tax,
                    "tax_amount": line_tax,
                    "line_total": line_total,
                    "vat_rate": float(vat_rate),
                    "price_display_mode": display_mode,
                    "commission_base": commission_base,
                    "helper_earnings": helper_earnings,
                    "platform_fee": platform_fee,
                    "applied_price_entry_id": price_entry.id,
                    "applied_commission_rule_id": rule.id,
                }
            )

        if customer_total != helper_total + platform_total and subtotal_before_tax_total != helper_total + platform_total:
            # Allow a 1 VND rounding difference later; for now enforce exact to keep deterministic.
            raise ConflictException("Breakdown does not reconcile (customer_total != helper_total + platform_total)")

        snapshot = BookingFinancialSnapshot(
            booking_id=payload.booking_id,
            currency=currency,
            customer_total=customer_total,
            subtotal_before_tax=subtotal_before_tax_total,
            tax_total=tax_total,
            helper_total=helper_total,
            platform_total=platform_total,
            applied_price_entry_id=applied_price_entry_id,
            applied_commission_rule_id=applied_commission_rule_id,
            line_items=line_breakdowns,
            computed_at=computed_at,
        )
        db.add(snapshot)
        await db.flush()
        await self._audit(
            db,
            actor,
            "booking_financial_snapshot",
            snapshot.id,
            "create",
            before=None,
            after=snapshot.to_dict(),
        )
        await db.commit()
        await db.refresh(snapshot)
        return snapshot

    def _split_commission(
        self,
        *,
        base_amount: int,
        helper_percent: Decimal,
        platform_percent: Decimal,
        fixed_helper_fee: int,
        fixed_platform_fee: int,
    ) -> tuple[int, int]:
        if base_amount < 0:
            raise ValidationException("base_amount must be non-negative")

        helper_share = (Decimal(base_amount) * helper_percent / Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        platform_share = (Decimal(base_amount) * platform_percent / Decimal(100)).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        helper_total = int(helper_share) + fixed_helper_fee
        platform_total = int(platform_share) + fixed_platform_fee

        if helper_total < 0 or platform_total < 0:
            raise ValidationException("Computed shares must be non-negative")

        return helper_total, platform_total

    async def _audit(
        self,
        db: AsyncSession,
        actor: User,
        entity_type: str,
        entity_id: str,
        action: str,
        *,
        before,
        after,
    ) -> None:
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


pricing_service = PricingService()

