import datetime
import uuid
from dataclasses import dataclass, replace
from typing import Any

from profile_service.core.exceptions import (
    PhoneAlreadyExistsError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from profile_service.core.phone import normalize_phone
from profile_service.entities.profiles import Profile
from profile_service.interfaces.profiles import IProfileRepo
from profile_service.schemas.profiles import ProfileCreate, ProfileUpdate


@dataclass(frozen=True)
class ProfileService:
    repo: IProfileRepo

    async def create_profile(
        self,
        user_id: uuid.UUID,
        data: ProfileCreate,
    ) -> Profile:
        existing_profile = await self.repo.get_by_user_id(user_id=user_id)

        if existing_profile is not None:
            raise ProfileAlreadyExistsError()

        normalized_phone = normalize_phone(data.phone)

        profile_with_phone = await self.repo.get_by_phone(
            phone=normalized_phone,
        )

        if profile_with_phone is not None:
            raise PhoneAlreadyExistsError()

        now = datetime.datetime.now(datetime.UTC)

        profile = Profile(
            id=uuid.uuid4(),
            user_id=user_id,
            phone=normalized_phone,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            created_at=now,
            updated_at=now,
        )

        profile_created = await self.repo.create_profile(profile=profile)

        return profile_created

    async def get_by_user_id(self, user_id: uuid.UUID) -> Profile:
        profile = await self.repo.get_by_user_id(user_id=user_id)
        if profile is None:
            raise ProfileNotFoundError()

        return profile

    async def update_profile(
        self,
        user_id: uuid.UUID,
        data: ProfileUpdate,
    ) -> Profile:
        profile = await self.repo.get_by_user_id(user_id=user_id)

        if profile is None:
            raise ProfileNotFoundError()

        changes = data.model_dump(exclude_unset=True)
        await self._prepare_phone_change(
            changes=changes,
            current_profile=profile,
        )
        updated_profile = replace(
            profile,
            **changes,
            updated_at=datetime.datetime.now(datetime.UTC),
        )

        return await self.repo.update_profile(profile=updated_profile)

    async def delete_profile(self, user_id: uuid.UUID) -> None:
        await self.repo.delete_profile(user_id=user_id)

    async def _prepare_phone_change(
        self,
        changes: dict[str, Any],
        current_profile: Profile,
    ) -> None:
        phone = changes.get("phone")

        if phone is None:
            return

        normalized_phone = normalize_phone(phone=phone)
        changes["phone"] = normalized_phone

        if normalized_phone == current_profile.phone:
            return

        existing_profile = await self.repo.get_by_phone(phone=normalized_phone)

        if existing_profile is not None:
            raise PhoneAlreadyExistsError()
