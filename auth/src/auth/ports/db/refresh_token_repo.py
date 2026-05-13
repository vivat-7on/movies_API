import uuid
from datetime import datetime
from typing import Protocol

from auth.models.models import RefreshToken


class IRefreshTokenRepo(Protocol):
    async def save(
        self,
        refresh_token_hash: str,
        user_id: uuid.UUID,
        expires_at: datetime,
        user_agent: str | None = None,
    ) -> None: ...

    async def get_by_hash(self, refresh_token_hash: str) -> RefreshToken | None: ...

    async def delete(self, token: RefreshToken) -> None: ...
