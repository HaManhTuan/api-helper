from collections import defaultdict
from datetime import datetime, timedelta
from hashlib import sha256
import csv
import io
from typing import Dict, List

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.booking_financial_snapshot import BookingFinancialSnapshot
from app.models.report_export_job import ReportExportJob
from app.models.user import User
from app.repositories.concrete.report_export_job_repository import report_export_job_repository


class AnalyticsService:
    async def bookings_timeseries(self, db: AsyncSession, *, start_at, end_at) -> List[dict]:
        rows = (
            await db.execute(
                select(Booking).where(
                    Booking.deleted_at.is_(None),
                    and_(Booking.created_at >= start_at, Booking.created_at <= end_at),
                )
            )
        ).scalars().all()

        buckets: Dict[str, dict] = defaultdict(lambda: {"created": 0, "completed": 0, "cancelled": 0})
        for item in rows:
            day = (item.created_at + timedelta(hours=7)).date().isoformat()
            buckets[day]["created"] += 1
            if item.status == "completed":
                buckets[day]["completed"] += 1
            if item.status == "cancelled":
                buckets[day]["cancelled"] += 1

        return [{"date": day, **vals} for day, vals in sorted(buckets.items(), key=lambda x: x[0])]

    async def supply_demand_kpis(self, db: AsyncSession, *, start_at, end_at) -> dict:
        users = (
            await db.execute(
                select(User).where(
                    User.deleted_at.is_(None),
                    and_(User.created_at >= start_at, User.created_at <= end_at),
                )
            )
        ).scalars().all()
        active_helpers = sum(1 for u in users if u.role == "helper" and u.status == "active")
        new_registrations = len(users)

        bookings = (
            await db.execute(
                select(Booking).where(
                    Booking.deleted_at.is_(None),
                    and_(Booking.created_at >= start_at, Booking.created_at <= end_at),
                )
            )
        ).scalars().all()
        accepted = sum(1 for b in bookings if b.helper_id is not None)
        completed = sum(1 for b in bookings if b.status == "completed")
        total = len(bookings)

        return {
            "active_helpers": active_helpers,
            "new_registrations": new_registrations,
            "accept_rate": (accepted / total) if total else 0.0,
            "completion_rate": (completed / total) if total else 0.0,
            "median_response_seconds": None,
        }

    async def revenue_report(self, db: AsyncSession, *, start_at, end_at, group_by=None) -> dict:
        snapshots = (
            await db.execute(
                select(BookingFinancialSnapshot).where(
                    BookingFinancialSnapshot.deleted_at.is_(None),
                    and_(BookingFinancialSnapshot.computed_at >= start_at, BookingFinancialSnapshot.computed_at <= end_at),
                )
            )
        ).scalars().all()

        summary = {
            "gmv_total": int(sum(int(s.customer_total or 0) for s in snapshots)),
            "platform_fee_total": int(sum(int(s.platform_total or 0) for s in snapshots)),
            "helper_earnings_total": int(sum(int(s.helper_total or 0) for s in snapshots)),
            "promotion_cost_total": int(sum(int(s.promotion_total or 0) for s in snapshots)),
        }

        groups: Dict[str, dict] = defaultdict(lambda: {"gmv_total": 0, "platform_fee_total": 0, "helper_earnings_total": 0, "promotion_cost_total": 0})
        if group_by:
            bookings_map = {
                b.id: b
                for b in (
                    await db.execute(select(Booking).where(Booking.deleted_at.is_(None)))
                ).scalars().all()
            }
            for snap in snapshots:
                booking = bookings_map.get(snap.booking_id)
                if not booking:
                    key = "unknown"
                elif group_by == "district":
                    key = str((booking.address_snapshot or {}).get("district", "unknown"))
                else:
                    key = "all"
                groups[key]["gmv_total"] += int(snap.customer_total or 0)
                groups[key]["platform_fee_total"] += int(snap.platform_total or 0)
                groups[key]["helper_earnings_total"] += int(snap.helper_total or 0)
                groups[key]["promotion_cost_total"] += int(snap.promotion_total or 0)

        return {
            "summary": summary,
            "groups": [{"key": key, **vals} for key, vals in sorted(groups.items(), key=lambda x: x[0])],
        }

    async def cohort_metrics(self, db: AsyncSession, *, start_at, end_at) -> dict:
        customers = (
            await db.execute(
                select(User).where(
                    User.deleted_at.is_(None),
                    User.role == "customer",
                    and_(User.created_at >= start_at, User.created_at <= end_at),
                )
            )
        ).scalars().all()
        customer_ids = [c.id for c in customers]
        bookings = (
            await db.execute(
                select(Booking).where(
                    Booking.deleted_at.is_(None),
                    Booking.customer_id.in_(customer_ids) if customer_ids else Booking.customer_id == "__none__",
                )
            )
        ).scalars().all()
        by_customer: Dict[str, int] = defaultdict(int)
        for b in bookings:
            by_customer[str(b.customer_id)] += 1

        signed = len(customers)
        converted = sum(1 for c in customers if by_customer.get(c.id, 0) >= 1)
        repeated = sum(1 for c in customers if by_customer.get(c.id, 0) >= 2)
        return {
            "signup_to_first_booking_rate": (converted / signed) if signed else 0.0,
            "repeat_customer_rate_monthly": (repeated / signed) if signed else 0.0,
        }

    async def create_export_job(self, db: AsyncSession, *, actor: User, payload) -> ReportExportJob:
        report = await self.revenue_report(db, start_at=payload.start_at, end_at=payload.end_at, group_by=None)
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["metric", "value"])
        for key, value in report["summary"].items():
            writer.writerow([key, value])
        content = out.getvalue()
        checksum = sha256(content.encode("utf-8")).hexdigest()

        job = ReportExportJob(
            report_type=payload.report_type,
            filters={"start_at": payload.start_at.isoformat(), "end_at": payload.end_at.isoformat()},
            status="completed",
            file_ref=content,
            checksum=checksum,
            requested_by=actor.id,
            completed_at=datetime.utcnow(),
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    async def get_export_job(self, db: AsyncSession, job_id: str) -> ReportExportJob:
        return await report_export_job_repository.get_by_id(db, job_id)


analytics_service = AnalyticsService()
