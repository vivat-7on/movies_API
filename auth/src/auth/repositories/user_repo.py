import uuid

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.models import User
from auth.ports.user_repo import IUserRepo


class UserRepo(IUserRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_login(self, login: str) -> User | None:
        stmt = select(User).where(User.login == login)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        stmt = select(exists().where(User.email == email))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create(
        self,
        login: str,
        password_hash: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        user = User(
            login=login,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        self.session.add(user)
        return user

    async def increase_token_version(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(token_version=User.token_version + 1)
        )
        await self.session.execute(stmt)
