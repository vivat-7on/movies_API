import uuid
from datetime import datetime
from typing import Protocol


class IRefreshTokenRepo(Protocol):
    async def save_refresh_token(
        self,
        refresh_token_hash: str,
        user_id: uuid.UUID,
        expires_at: datetime,
        user_agent: str | None = None,
    ) -> None: ...
