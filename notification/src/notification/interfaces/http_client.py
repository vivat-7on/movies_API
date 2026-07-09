import uuid
from typing import Protocol

from notification.dtos.user import UserData


class IAuthClient(Protocol):
    async def get_user_by_id(self, user_id: uuid.UUID) -> UserData: ...
