import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.models import RefreshToken
from auth.ports.refresh_token_repo import IRefreshTokenRepo


class RefreshTokenRepo(IRefreshTokenRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(
        self,
        refresh_token_hash: str,
        user_id: uuid.UUID,
        expires_at: datetime,
        user_agent: str | None = None,
    ) -> None:
        token = RefreshToken(
            token_hash=refresh_token_hash,
            user_id=user_id,
            expires_at=expires_at,
            user_agent=user_agent,
        )
        self.session.add(token)

    async def get_by_hash(self, refresh_token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == refresh_token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, token: RefreshToken) -> None:
        await self.session.delete(token)
