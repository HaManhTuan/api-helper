from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.helper_document import HelperDocument
from app.models.helper_document_type import HelperDocumentType
from app.models.helper_profile import HelperProfile
from app.models.user import User
from app.services.helper_moderation_service import helper_moderation_service


@pytest.mark.asyncio
async def test_helper_missing_required_document_is_not_eligible(db: AsyncSession) -> None:
    helper = User(email="helper-kyc@test.local", role="helper", status="active", password="secret")
    db.add(helper)
    await db.flush()
    db.add(
        HelperProfile(
            user_id=helper.id,
            display_name="Helper KYC",
            skills=[],
            service_area={"city": "hanoi"},
            approval_status="approved",
            approved_at=datetime.utcnow(),
        )
    )
    db.add(HelperDocumentType(code="citizen_id", name="Citizen ID", required=True, active=True, sort_order=1))
    await db.commit()

    eligibility = await helper_moderation_service.get_eligibility(db, helper.id)
    assert eligibility["eligible"] is False
    assert eligibility["reason_code"] == "missing_required_kyc"
    assert "citizen_id" in eligibility["missing_required_document_types"]


@pytest.mark.asyncio
async def test_helper_with_required_document_is_eligible(db: AsyncSession) -> None:
    helper = User(email="helper-eligible@test.local", role="helper", status="active", password="secret")
    db.add(helper)
    await db.flush()
    db.add(
        HelperProfile(
            user_id=helper.id,
            display_name="Helper Eligible",
            skills=[],
            service_area={"city": "hanoi"},
            approval_status="approved",
            approved_at=datetime.utcnow(),
        )
    )
    db.add(HelperDocumentType(code="citizen_id", name="Citizen ID", required=True, active=True, sort_order=1))
    db.add(
        HelperDocument(
            helper_id=helper.id,
            document_type="citizen_id",
            storage_ref="helpers/test/citizen_id.pdf",
            mime_type="application/pdf",
            file_size_bytes=1000,
            status="approved",
        )
    )
    await db.commit()

    eligibility = await helper_moderation_service.get_eligibility(db, helper.id)
    assert eligibility["eligible"] is True
    assert eligibility["missing_required_document_types"] == []
