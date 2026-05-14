import http

import httpx
from attr import frozen
from pydantic import ValidationError

from auth.core.config import YandexOAuthSettings
from auth.dtos.token import OAuthTokensDTO, YandexUserInfoDTO


@frozen
class YandexClient:
    settings: YandexOAuthSettings

    async def exchange_code_for_token(
        self,
        code: str,
    ) -> OAuthTokensDTO | None:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    self.settings.YANDEX_TOKEN_URI,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.settings.YANDEX_REDIRECT_URI,
                    },
                    auth=(
                        self.settings.YANDEX_CLIENT_ID,
                        self.settings.YANDEX_CLIENT_SECRET,
                    ),
                )
        except httpx.HTTPError:
            return None

        if response.status_code != http.HTTPStatus.OK:
            return None

        try:
            return OAuthTokensDTO(**response.json())
        except (ValueError, ValidationError):
            return None

    async def get_user_info(
        self,
        access_token: str,
    ) -> YandexUserInfoDTO | None:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    self.settings.YANDEX_USER_INFO_URI,
                    params={"format": "json"},
                    headers={"Authorization": f"OAuth {access_token}"},
                )
        except httpx.HTTPError:
            return None

        if response.status_code != http.HTTPStatus.OK:
            return None
        try:
            return YandexUserInfoDTO(**response.json())
        except (ValueError, ValidationError):
            return None
