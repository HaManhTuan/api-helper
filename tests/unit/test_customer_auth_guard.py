import pytest

from app.exceptions import ForbiddenException
from app.models.user import User
from app.utils.auth import get_current_customer_user


@pytest.mark.asyncio
async def test_get_current_customer_user_blocks_suspended_customer() -> None:
    suspended_customer = User(email="suspended@test.local", role="customer", status="suspended", password="secret")
    with pytest.raises(ForbiddenException) as exc:
        await get_current_customer_user(current_user=suspended_customer)
    assert exc.value.status_code == 403
    assert exc.value.details.get("reason_code") == "customer_suspended"
