import uuid
from typing import Protocol


class IUserRoleRepo(Protocol):
    async def assign_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> None: ...
