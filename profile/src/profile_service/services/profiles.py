import datetime
import uuid
from dataclasses import dataclass, replace
from typing import Any

from profile_service.core.exceptions import ProfileNotFoundError
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
        now = datetime.datetime.now(datetime.UTC)

        profile = Profile(
            id=uuid.uuid4(),
            user_id=user_id,
            phone=normalize_phone(data.phone),
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            created_at=now,
            updated_at=now,
        )

        return await self.repo.create_profile(profile=profile)

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
        self._normalize_phone_change(changes=changes)

        updated_profile = replace(
            profile,
            **changes,
            updated_at=datetime.datetime.now(datetime.UTC),
        )

        return await self.repo.update_profile(profile=updated_profile)

    async def delete_profile(self, user_id: uuid.UUID) -> None:
        await self.repo.delete_profile(user_id=user_id)

    @staticmethod
    def _normalize_phone_change(changes: dict[str, Any]) -> None:
        phone = changes.get("phone")

        if phone is None:
            return

        changes["phone"] = normalize_phone(phone=phone)
