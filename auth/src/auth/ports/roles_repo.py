import uuid
from typing import Protocol


class IRoleRepo(Protocol):
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[str]: ...

    async def get_id_by_name(self, name: str) -> uuid.UUID | None: ...
