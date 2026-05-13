import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.models import SocialAccount
from auth.ports.db.social_account_repo import ISocialAccountRepo


class SocialAccountRepo(ISocialAccountRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_provider_and_social_id(
        self,
        social_id: str,
        provider: str,
    ) -> SocialAccount | None:
        stmt = (
            select(SocialAccount)
            .where(SocialAccount.social_id == social_id)
            .where(SocialAccount.provider == provider)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        social_id: str,
        provider: str,
        user_id: uuid.UUID,
    ) -> SocialAccount:
        social_account = SocialAccount(
            social_id=social_id,
            provider=provider,
            user_id=user_id,
        )
        self.session.add(social_account)
        return social_account
