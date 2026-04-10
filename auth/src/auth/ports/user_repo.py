from typing import Protocol

from auth.models.models import User


class IUserRepo(Protocol):
    async def get_user_by_login(self, login: str) -> User | None: ...

    async def email_exist(self, email: str) -> bool: ...

    async def create_user(
        self,
        login: str,
        password_hash: str,
        email: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> None: ...
