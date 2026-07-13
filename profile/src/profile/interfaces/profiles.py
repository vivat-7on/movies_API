import uuid
from profile.entities.profiles import Profile
from typing import Protocol


class IProfileRepo(Protocol):
    async def create_profile(self, profile: Profile) -> Profile: ...

    async def get_by_user_id(self, user_id: uuid.UUID) -> Profile | None: ...

    async def get_by_phone(self, phone: str) -> Profile | None: ...
