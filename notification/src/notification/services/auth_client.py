import uuid
from dataclasses import dataclass

import httpx

from notification.core.auth_settings import AuthSettings


@dataclass(frozen=True)
class UserData:
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str


@dataclass(frozen=True)
class AuthClient:
    auth_settings: AuthSettings

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserData:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.auth_settings.url.format(user_id=user_id),
                headers={"X-Request-Id": str(uuid.uuid4())},
                timeout=5.0,
            )
            response.raise_for_status()
            data = response.json()

        return UserData(
            id=user_id,
            email=data["email"],
            first_name=data.get("first_name") or data.get("login") or data["email"],
            last_name=data.get("last_name", ""),
        )
