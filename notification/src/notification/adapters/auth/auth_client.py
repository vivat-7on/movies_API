import uuid

import httpx

from notification.core.auth_settings import AuthSettings
from notification.dtos.user import UserData
from notification.interfaces.http_client import IAuthClient


class AuthClient(IAuthClient):
    def __init__(self, auth_settings: AuthSettings):
        self.auth_settings = auth_settings

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserData:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.auth_settings.url.format(user_id=user_id),
                headers={
                    "X-Request-Id": str(uuid.uuid4()),
                    "X-Service-Token": self.auth_settings.AUTH_SERVICE_TOKEN,
                },
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
