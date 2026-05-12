import uuid
from typing import Protocol

from auth.models.models import SocialAccount


class ISocialAccountRepo(Protocol):
    async def get_by_provider_and_social_id(
        self,
        social_id: str,
        provider: str,
    ) -> SocialAccount | None: ...

    async def create(
        self,
        social_id: str,
        provider: str,
        user_id: uuid.UUID,
    ) -> SocialAccount: ...
