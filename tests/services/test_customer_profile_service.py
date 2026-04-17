import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.customer_portal import (
    CustomerProfileUpdateRequest,
    SavedAddressCreateRequest,
    SavedAddressUpdateRequest,
)
from app.services.customer_profile_service import customer_profile_service


@pytest.mark.asyncio
async def test_customer_profile_update_and_saved_address_crud(db: AsyncSession) -> None:
    customer = User(email="customer-profile@test.local", role="customer", status="active", password="secret")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    profile = await customer_profile_service.get_or_create_profile(db, customer)
    assert profile.user_id == customer.id

    updated_profile = await customer_profile_service.update_profile(
        db, customer, CustomerProfileUpdateRequest(full_name="Nguyen Van A", contact_phone="0901234567")
    )
    assert updated_profile.full_name == "Nguyen Van A"

    addr_1 = await customer_profile_service.create_address(
        db,
        customer,
        SavedAddressCreateRequest(
            label="Nha",
            line="123 Pho Hue",
            district="Hai Ba Trung",
            city="Hanoi",
            is_default=True,
        ),
    )
    assert addr_1.is_default is True

    addr_2 = await customer_profile_service.create_address(
        db,
        customer,
        SavedAddressCreateRequest(
            label="VP",
            line="1 Tran Duy Hung",
            district="Cau Giay",
            city="Hanoi",
            is_default=False,
        ),
    )
    assert addr_2.is_default is False

    updated_addr_2 = await customer_profile_service.update_address(
        db,
        customer,
        addr_2.id,
        SavedAddressUpdateRequest(is_default=True),
    )
    assert updated_addr_2.is_default is True

    rows = await customer_profile_service.list_addresses(db, customer)
    assert len(rows) == 2
    assert sum(1 for item in rows if item.is_default) == 1
