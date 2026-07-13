import dataclasses
import datetime
import uuid
from dataclasses import dataclass
from profile.core.exceptions import (
    InvalidPhoneNumberError,
    PhoneAlreadyExistsError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from profile.core.utils import normalize_phone
from profile.entities.profiles import Profile
from profile.interfaces.profiles import IProfileRepo
from profile.schemas.profiles import ProfileCreate, ProfileUpdate


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

        if "phone" in changes:
            phone = changes["phone"]

            if phone is None:
                raise InvalidPhoneNumberError()

            normalized_phone = normalize_phone(phone=phone)

            if normalized_phone != profile.phone:
                profile_with_phone = await self.repo.get_by_phone(
                    phone=normalized_phone,
                )

                if profile_with_phone is not None:
                    raise PhoneAlreadyExistsError()

            changes["phone"] = normalized_phone
        now = datetime.datetime.now(datetime.UTC)

        updated_profile = dataclasses.replace(
            profile,
            **changes,
            updated_at=now,
        )

        return await self.repo.update_profile(profile=updated_profile)

    async def delete_profile(self, user_id: uuid.UUID) -> None:
        await self.repo.delete_profile(user_id=user_id)
