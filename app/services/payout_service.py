from datetime import datetime
from io import StringIO
import csv
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.payout_batch import PayoutBatch
from app.models.payout_line import PayoutLine
from app.models.staff_audit_log import StaffAuditLog
from app.models.user import User
from app.repositories.concrete.payout_batch_repository import payout_batch_repository
from app.repositories.concrete.payout_line_repository import payout_line_repository


class PayoutService:
    VALID_APPROVE_STATUSES = {"pending_approval"}
    VALID_MARK_PAID_STATUSES = {"approved"}

    async def generate_batch(self, db: AsyncSession, actor: User, payload) -> PayoutBatch:
        if payload.period_end <= payload.period_start:
            raise ValidationException("period_end must be greater than period_start")

        base_rows = await payout_line_repository.aggregate_base_amounts(
            db, period_start=payload.period_start, period_end=payload.period_end
        )
        adjustment_rows = await payout_line_repository.aggregate_adjustments(
            db, period_start=payload.period_start, period_end=payload.period_end
        )

        merged_helper_ids = sorted(set(base_rows.keys()) | set(adjustment_rows.keys()))
        batch = PayoutBatch(
            period_start=payload.period_start,
            period_end=payload.period_end,
            status="pending_approval",
            currency=payload.currency,
            total_lines=0,
            total_amount=0,
        )
        db.add(batch)
        await db.flush()

        total_amount = 0
        total_lines = 0
        for helper_id in merged_helper_ids:
            base = base_rows.get(helper_id, {})
            base_amount = int(base.get("base_amount", 0))
            adjustment_amount = int(adjustment_rows.get(helper_id, 0))
            total = base_amount + adjustment_amount
            line = PayoutLine(
                payout_batch_id=batch.id,
                helper_id=helper_id,
                currency=payload.currency,
                base_amount=base_amount,
                adjustment_amount=adjustment_amount,
                total_amount=total,
                booking_ids=base.get("booking_ids", []),
                booking_count=int(base.get("booking_count", 0)),
            )
            db.add(line)
            total_amount += total
            total_lines += 1

        batch.total_lines = total_lines
        batch.total_amount = total_amount
        db.add(batch)
        await self._audit(
            db,
            actor_user_id=actor.id,
            target_user_id=actor.id,
            action="payout:generate",
            details=f"batch_id={batch.id};lines={total_lines};total_amount={total_amount}",
        )
        await db.commit()
        await db.refresh(batch)
        return batch

    async def list_batches(self, db: AsyncSession, *, status: Optional[str]) -> List[PayoutBatch]:
        return await payout_batch_repository.list_batches(db, status=status)

    async def get_batch_detail(self, db: AsyncSession, batch_id: str) -> Tuple[PayoutBatch, List[PayoutLine]]:
        batch = await payout_batch_repository.get_by_id(db, batch_id)
        if batch is None:
            raise NotFoundException("Payout batch not found")
        lines = await payout_line_repository.list_by_batch(db, payout_batch_id=batch.id)
        return batch, lines

    async def approve_batch(self, db: AsyncSession, actor: User, batch_id: str) -> PayoutBatch:
        batch = await payout_batch_repository.get_by_id(db, batch_id)
        if batch is None:
            raise NotFoundException("Payout batch not found")
        if batch.status not in self.VALID_APPROVE_STATUSES:
            raise ConflictException("Batch cannot be approved in current status")
        batch.status = "approved"
        batch.approved_by = actor.id
        batch.approved_at = datetime.utcnow()
        db.add(batch)
        await self._audit(
            db,
            actor_user_id=actor.id,
            target_user_id=actor.id,
            action="payout:approve",
            details=f"batch_id={batch.id};status=approved",
        )
        await db.commit()
        await db.refresh(batch)
        return batch

    async def mark_batch_paid(self, db: AsyncSession, actor: User, batch_id: str, payload) -> PayoutBatch:
        batch = await payout_batch_repository.get_by_id(db, batch_id)
        if batch is None:
            raise NotFoundException("Payout batch not found")
        if batch.status not in self.VALID_MARK_PAID_STATUSES:
            raise ConflictException("Batch cannot be marked in current status")
        if payload.status == "failed" and not payload.failure_reason:
            raise ValidationException("failure_reason is required when status is failed")
        batch.status = payload.status
        batch.paid_by = actor.id
        batch.paid_at = datetime.utcnow()
        batch.failure_reason = payload.failure_reason
        db.add(batch)
        await self._audit(
            db,
            actor_user_id=actor.id,
            target_user_id=actor.id,
            action="payout:mark_paid",
            details=f"batch_id={batch.id};status={payload.status}",
        )
        await db.commit()
        await db.refresh(batch)
        return batch

    async def export_batch_csv(self, db: AsyncSession, batch_id: str) -> dict:
        batch, lines = await self.get_batch_detail(db, batch_id)
        if batch.status not in {"approved", "paid"}:
            raise ConflictException("Batch must be approved before export")

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["helper_id", "currency", "base_amount", "adjustment_amount", "total_amount", "booking_count"])
        for line in lines:
            writer.writerow(
                [
                    line.helper_id,
                    line.currency,
                    int(line.base_amount),
                    int(line.adjustment_amount),
                    int(line.total_amount),
                    int(line.booking_count),
                ]
            )

        filename = f"payout_batch_{batch.id}.csv"
        return {"payout_batch_id": batch.id, "filename": filename, "csv_content": output.getvalue()}

    async def _audit(self, db: AsyncSession, actor_user_id: str, target_user_id: str, action: str, details: str) -> None:
        db.add(
            StaffAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action=action,
                details=details,
            )
        )


payout_service = PayoutService()
