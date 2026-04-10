from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.models import User
from auth.ports.user_repo import IUserRepo


class UserRepo(IUserRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_login(self, login: str) -> User | None:
        stmt = select(User).where(User.login == login)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exist(self, email: str) -> bool:
        stmt = select(exists().where(User.email == email))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create_user(
        self,
        login: str,
        password_hash: str,
        email: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> None:
        user = User(
            login=login,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        self.session.add(user)
        await self.session.commit()
