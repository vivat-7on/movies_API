import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from profile_service.core.exceptions import (
    PhoneAlreadyExistsError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from profile_service.db.tables import ProfileTable
from profile_service.entities.profiles import Profile
from profile_service.interfaces.profiles import IProfileRepo


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


def _get_constraint_name(exc: IntegrityError) -> str | None:
    current: BaseException | None = exc.orig

    while current is not None:
        constraint_name = getattr(current, "constraint_name", None)

        if constraint_name is not None:
            return constraint_name

        current = current.__cause__

    return None


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
            constraint_name = _get_constraint_name(exc)

            if constraint_name == "uq_profiles_phone":
                raise PhoneAlreadyExistsError() from exc

            if constraint_name == "uq_profiles_user_id":
                raise ProfileAlreadyExistsError() from exc

            raise

        return _to_entity(table=profile_table)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Profile | None:
        stmt = select(ProfileTable).where(ProfileTable.user_id == user_id)

        result = await self.session.execute(stmt)
        profile_table = result.scalar_one_or_none()

        if profile_table is None:
            return None

        return _to_entity(table=profile_table)

    async def update_profile(self, profile: Profile) -> Profile:
        stmt = (
            update(ProfileTable)
            .where(ProfileTable.user_id == profile.user_id)
            .values(
                phone=profile.phone,
                first_name=profile.first_name,
                middle_name=profile.middle_name,
                last_name=profile.last_name,
                updated_at=profile.updated_at,
            )
            .returning(ProfileTable)
        )
        try:
            result = await self.session.execute(stmt)
        except IntegrityError as exc:
            constraint_name = _get_constraint_name(exc)

            if constraint_name == "uq_profiles_phone":
                raise PhoneAlreadyExistsError() from exc
            raise

        profile_table = result.scalar_one_or_none()

        if profile_table is None:
            raise ProfileNotFoundError()

        return _to_entity(table=profile_table)

    async def delete_profile(self, user_id: uuid.UUID) -> None:
        stmt = delete(ProfileTable).where(ProfileTable.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.flush()
