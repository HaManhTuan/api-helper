from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException, ValidationException
from app.models.customer_profile import CustomerProfile
from app.models.saved_address import SavedAddress
from app.models.user import User
from app.repositories.concrete.customer_profile_repository import customer_profile_repository
from app.repositories.concrete.saved_address_repository import saved_address_repository


class CustomerProfileService:
    HANOI_CITY_ALIASES = {"hanoi", "ha noi", "ha_noi", "hà nội", "ha-noi"}

    async def get_or_create_profile(self, db: AsyncSession, customer: User) -> CustomerProfile:
        profile = await customer_profile_repository.get_by_user_id(db, customer.id)
        if profile:
            return profile
        profile = CustomerProfile(
            user_id=customer.id,
            full_name=None,
            contact_phone=customer.phone,
            preferences={},
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile

    async def update_profile(self, db: AsyncSession, customer: User, payload) -> CustomerProfile:
        profile = await self.get_or_create_profile(db, customer)
        if payload.full_name is not None:
            profile.full_name = payload.full_name
        if payload.contact_phone is not None:
            profile.contact_phone = payload.contact_phone
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile

    async def list_addresses(self, db: AsyncSession, customer: User) -> list[SavedAddress]:
        return await saved_address_repository.list_by_customer(db, customer.id)

    async def create_address(self, db: AsyncSession, customer: User, payload) -> SavedAddress:
        self._validate_hanoi_city(payload.city)
        address = SavedAddress(
            customer_id=customer.id,
            label=payload.label,
            line=payload.line,
            district=payload.district,
            city=payload.city,
            latitude=payload.latitude,
            longitude=payload.longitude,
            is_default=bool(payload.is_default),
        )
        db.add(address)
        await db.flush()
        if address.is_default:
            await saved_address_repository.clear_default_for_customer(db, customer.id, keep_address_id=address.id)
        elif not await self._has_default_address(db, customer.id):
            address.is_default = True
            db.add(address)
        await db.commit()
        await db.refresh(address)
        return address

    async def update_address(self, db: AsyncSession, customer: User, address_id: str, payload) -> SavedAddress:
        address = await saved_address_repository.get_by_id_and_customer(db, address_id, customer.id)
        if address is None:
            raise NotFoundException("Saved address not found")

        if payload.label is not None:
            address.label = payload.label
        if payload.line is not None:
            address.line = payload.line
        if payload.district is not None:
            address.district = payload.district
        if payload.city is not None:
            self._validate_hanoi_city(payload.city)
            address.city = payload.city
        if payload.latitude is not None:
            address.latitude = payload.latitude
        if payload.longitude is not None:
            address.longitude = payload.longitude
        if payload.is_default is not None:
            address.is_default = bool(payload.is_default)

        db.add(address)
        await db.flush()
        if address.is_default:
            await saved_address_repository.clear_default_for_customer(db, customer.id, keep_address_id=address.id)
        elif not await self._has_default_address(db, customer.id):
            address.is_default = True
            db.add(address)
        await db.commit()
        await db.refresh(address)
        return address

    async def delete_address(self, db: AsyncSession, customer: User, address_id: str) -> None:
        address = await saved_address_repository.get_by_id_and_customer(db, address_id, customer.id)
        if address is None:
            raise NotFoundException("Saved address not found")
        was_default = bool(address.is_default)
        await saved_address_repository.delete(db, id=address.id, hard_delete=False)
        if was_default:
            addresses = await saved_address_repository.list_by_customer(db, customer.id)
            if addresses:
                candidate = addresses[0]
                candidate.is_default = True
                db.add(candidate)
        await db.commit()

    async def _has_default_address(self, db: AsyncSession, customer_id: str) -> bool:
        rows = await saved_address_repository.list_by_customer(db, customer_id)
        return any(bool(r.is_default) for r in rows)

    def _validate_hanoi_city(self, city: str) -> None:
        normalized = city.strip().lower()
        if normalized not in self.HANOI_CITY_ALIASES:
            raise ValidationException("Address city must be in Hanoi service area")


customer_profile_service = CustomerProfileService()
