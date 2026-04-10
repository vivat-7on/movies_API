from datetime import datetime
from typing import Protocol


class IRefreshTokenRepo(Protocol):
    async def save_refresh_token(
        self,
        refresh_token: str,
        user_id: str,
        expires_at: float,
        created_at: datetime,
        user_agent: str | None,
    ) -> None: ...
