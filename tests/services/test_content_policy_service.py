import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.content import ContentBlockUpsertRequest
from app.services.content_policy_service import content_policy_service


@pytest.mark.asyncio
async def test_publish_and_fetch_content_block(db: AsyncSession) -> None:
    admin = User(email="admin-content@test.local", role="admin", status="active", password="secret")
    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    created = await content_policy_service.upsert_block(
        db,
        admin,
        ContentBlockUpsertRequest(
            key="cancellation_policy",
            locale="vi",
            title="Policy",
            body="No-show policy",
            content_format="markdown",
            version="v1",
            status="published",
        ),
    )
    assert created.status == "published"

    published = await content_policy_service.get_published(db, key="cancellation_policy", locale="vi")
    assert published.id == created.id
