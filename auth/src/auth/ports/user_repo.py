import uuid
from typing import Protocol

from auth.models.models import User


class IUserRepo(Protocol):
    async def get_by_login(self, login: str) -> User | None: ...

    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    async def email_exists(self, email: str) -> bool: ...

    async def create(
        self,
        login: str,
        password_hash: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User: ...

    async def increase_token_version(self, user_id: uuid.UUID) -> None: ...
