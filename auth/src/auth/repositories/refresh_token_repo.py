from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from auth.ports.refresh_token_repo import IRefreshTokenRepo


class RefreshTokenRepo(IRefreshTokenRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_refresh_token(
        self,
        refresh_token: str,
        user_id: str,
        expires_at: float,
        created_at: datetime,
        user_agent: str,
    ) -> None: ...
