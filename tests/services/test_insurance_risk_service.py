from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.service_offering import ServiceOffering
from app.models.user import User
from app.schemas.insurance import (
    InsuranceClaimCreateRequest,
    InsuranceClaimUpdateRequest,
    InsuranceEnrollmentUpsertRequest,
    InsuranceProductUpsertRequest,
    ServiceInsuranceRuleUpdateRequest,
)
from app.services.insurance_risk_service import insurance_risk_service


@pytest.mark.asyncio
async def test_insurance_product_enrollment_claim_and_service_rule(db: AsyncSession) -> None:
    admin = User(email="admin-ins@test.local", role="admin", status="active", password="secret")
    helper = User(email="helper-ins@test.local", role="helper", status="active", password="secret")
    customer = User(email="customer-ins@test.local", role="customer", status="active", password="secret")
    db.add_all([admin, helper, customer])
    await db.flush()

    service = ServiceOffering(code="svc-ins-test", name="Insurance Test Service", unit="hour", active=True, tags=[], meta={})
    db.add(service)
    await db.flush()

    booking = Booking(
        customer_id=customer.id,
        helper_id=helper.id,
        quote_id="Q-INS-1",
        status="completed",
        scheduled_start=datetime.utcnow() - timedelta(days=1),
        scheduled_end=datetime.utcnow(),
        address_snapshot={"city": "hanoi"},
    )
    db.add(booking)
    await db.commit()

    product = await insurance_risk_service.upsert_product(
        db,
        admin,
        None,
        InsuranceProductUpsertRequest(
            name="Basic Coverage",
            description="desc",
            coverage_summary="summary",
            premium_model="per_job",
            active=True,
        ),
    )
    assert product.name == "Basic Coverage"

    enrollment = await insurance_risk_service.upsert_enrollment(
        db,
        admin,
        None,
        InsuranceEnrollmentUpsertRequest(
            helper_id=helper.id,
            product_id=product.id,
            status="active",
            effective_from=datetime.utcnow() - timedelta(days=1),
            effective_to=datetime.utcnow() + timedelta(days=30),
        ),
    )
    assert enrollment.status == "active"

    claim = await insurance_risk_service.create_claim(
        db,
        admin,
        InsuranceClaimCreateRequest(
            booking_id=booking.id,
            reporter_role="customer",
            description="incident",
            severity="high",
        ),
    )
    assert claim.status == "opened"

    updated = await insurance_risk_service.update_claim(
        db, admin, claim.id, InsuranceClaimUpdateRequest(status="under_review", resolution_notes="check")
    )
    assert updated.status == "under_review"

    service_rule = await insurance_risk_service.update_service_rule(
        db,
        admin,
        service.id,
        ServiceInsuranceRuleUpdateRequest(insurance_required=True, insurance_enforcement="hard"),
    )
    assert bool(service_rule.insurance_required) is True
