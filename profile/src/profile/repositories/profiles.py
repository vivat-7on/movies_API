import uuid
from profile.core.exceptions import (
    PhoneAlreadyExistsError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from profile.db.tables import ProfileTable
from profile.entities.profiles import Profile
from profile.interfaces.profiles import IProfileRepo

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class ProfileRepo(IProfileRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_profile(self, profile: Profile) -> Profile:
        profile_table = ProfileTable(
            id=profile.id,
            user_id=profile.user_id,
            phone=profile.phone,
            first_name=profile.first_name,
            middle_name=profile.middle_name,
            last_name=profile.last_name,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

        self.session.add(profile_table)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            constraint_name = self._get_constraint_name(exc)

            if constraint_name == "uq_profiles_phone":
                raise PhoneAlreadyExistsError() from exc

            if constraint_name == "uq_profiles_user_id":
                raise ProfileAlreadyExistsError() from exc

            raise

        return self._to_entity(table=profile_table)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Profile | None:
        stmt = select(ProfileTable).where(ProfileTable.user_id == user_id)

        result = await self.session.execute(stmt)
        profile_table = result.scalar_one_or_none()

        if profile_table is None:
            return None

        return self._to_entity(table=profile_table)

    async def get_by_phone(self, phone: str) -> Profile | None:
        stmt = select(ProfileTable).where(ProfileTable.phone == phone)
        result = await self.session.execute(stmt)
        profile_table = result.scalar_one_or_none()
        if profile_table is None:
            return None
        return self._to_entity(table=profile_table)

    async def update_profile(self, profile: Profile) -> Profile:
        stmt = select(ProfileTable).where(
            ProfileTable.user_id == profile.user_id,
        )
        result = await self.session.execute(stmt)
        profile_table = result.scalar_one_or_none()

        if profile_table is None:
            raise ProfileNotFoundError()

        profile_table.phone = profile.phone
        profile_table.first_name = profile.first_name
        profile_table.middle_name = profile.middle_name
        profile_table.last_name = profile.last_name
        profile_table.updated_at = profile.updated_at

        try:
            await self.session.flush()
        except IntegrityError as exc:
            constraint_name = self._get_constraint_name(exc)
            if constraint_name == "uq_profiles_phone":
                raise PhoneAlreadyExistsError() from exc

            raise

        await self.session.refresh(profile_table)

        return self._to_entity(table=profile_table)

    async def delete_profile(self, user_id: uuid.UUID) -> None:
        stmt = delete(ProfileTable).where(ProfileTable.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.flush()

    @staticmethod
    def _to_entity(table: ProfileTable) -> Profile:
        return Profile(
            id=table.id,
            user_id=table.user_id,
            phone=table.phone,
            first_name=table.first_name,
            middle_name=table.middle_name,
            last_name=table.last_name,
            created_at=table.created_at,
            updated_at=table.updated_at,
        )

    @staticmethod
    def _get_constraint_name(exc: IntegrityError) -> str | None:
        current: BaseException | None = exc.orig

        while current is not None:
            constraint_name = getattr(current, "constraint_name", None)

            if constraint_name is not None:
                return constraint_name

            current = current.__cause__

        return None
