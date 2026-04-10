import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from auth.core.hashing import hash_password
from auth.models.models import User
from auth.ports.user_repo import IUserRepo


class UserRepo(IUserRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_login(self, login: str) -> User | None:
        return User(
            id=uuid.uuid4(),
            login=login,
            password_hash=hash_password("tests"),
            first_name="test_first",
            last_name="test_last",
            token_version=1,
            email="test_email",
        )
