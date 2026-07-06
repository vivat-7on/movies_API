import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class UserData:
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str


@dataclass(frozen=True)
class AuthClient:
    async def get_user_by_id(self, user_id: uuid.UUID) -> UserData:
        return UserData(
            id=user_id,
            email="test@example.com",
            first_name="Valerii",
            last_name="Semenov",
        )
