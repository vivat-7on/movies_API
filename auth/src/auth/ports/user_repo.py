from typing import Protocol

from auth.models.models import User


class IUserRepo(Protocol):
    async def get_user_by_login(self, login: str) -> User | None: ...
